"""
Create dummy robots so we can use vex-aim-tools classes without
having to connect to a real robot.
"""

import asyncio
import math

import numpy as np
import vex

from .aim_kin import AIMKinematics
from .camera import Camera
from .evbase import EventRouter
from .openai_client import OpenAIClient
from .particle import SLAMParticleFilter
from .path_planner import PathPlanner
from .rrt import RRT
from .thesaurus import Thesaurus
from .utils import Pose, PoseEstimate
from .worldmap import WorldMap


class SimRobot0():
    class Inertial():
        def get_heading(self): return 0

    def __init__(self):
        self.inertial = self.Inertial()

    def get_x_position(self): return 0
    def get_y_position(self): return 0


class _BackendSpeechListener:
    def __init__(self, thesaurus=None):
        self.thesaurus = thesaurus or Thesaurus()
        self.enabled = True
        self.paused = False

    def start(self):
        return

    def disable(self):
        self.enabled = False

    def enable(self):
        self.enabled = True
        self.paused = False

    def pause(self):
        self.paused = True

    def unpause(self):
        self.paused = False


class _BackendActuator:
    class ActuatorLocked(Exception):
        pass

    class ActuatorNotHeld(Exception):
        pass

    def __init__(self, robot, name):
        self.robot = robot
        self.name = name
        self.holder = None
        self.started = False

    def lock(self, node):
        if self.holder is None or self.holder is node:
            self.holder = node
            return True
        raise self.ActuatorLocked(f"{self.name} locked by {self.holder}")

    def unlock(self, node):
        if self.holder is node:
            self.holder = None
        else:
            raise self.ActuatorNotHeld()

    def unlock_if_held(self, node):
        if self.holder is node:
            self.holder = None

    def clear(self):
        self.holder = None
        self.started = False

    def status_update(self):
        return


class _BackendDriveActuator(_BackendActuator):
    def __init__(self, robot):
        super().__init__(robot, "drive")

    def _finish(self, node):
        node.complete()

    def _move_relative(self, distance_mm, angle_offset_deg):
        absolute_angle = self.robot.pose.theta + math.radians(angle_offset_deg)
        self.robot.pose.x += distance_mm * math.cos(absolute_angle)
        self.robot.pose.y += distance_mm * math.sin(absolute_angle)
        self.robot.robot0._x = -self.robot.pose.y
        self.robot.robot0._y = self.robot.pose.x
        self.robot.robot0._stopped = True

    def turn(self, node, angle_rads, turn_speed=None):
        self.lock(node)
        self.robot.pose.theta += angle_rads
        self.robot.robot0.inertial._heading = (-math.degrees(self.robot.pose.theta)) % 360
        self.robot.robot0._stopped = True
        self._finish(node)

    def forward(self, node, distance_mm, drive_speed=None):
        self.lock(node)
        self._move_relative(distance_mm, 0)
        self._finish(node)

    def sideways(self, node, distance_mm, drive_speed=None):
        self.lock(node)
        self._move_relative(distance_mm, -90)
        self._finish(node)

    def move_for(self, node, distance_mm, angle_deg, drive_speed=None):
        self.lock(node)
        self._move_relative(distance_mm, angle_deg)
        self._finish(node)

    def move_at(self, node, angle_deg, drive_speed=None):
        self.lock(node)
        self.robot.robot0._stopped = False
        self._finish(node)

    def move_with_vectors(self, node, xvel, yvel, rvel):
        self.lock(node)
        self.robot.robot0._stopped = False
        self._finish(node)

    def spin_wheels(self, node, left_vel, right_vel, back_vel):
        self.lock(node)
        self.robot.robot0._stopped = False
        self._finish(node)

    def stop(self):
        self.robot.robot0._stopped = True


class _BackendSoundActuator(_BackendActuator):
    def __init__(self, robot):
        super().__init__(robot, "sound")

    def _finish(self, node):
        node.complete()

    def say_text(self, node, text):
        self.lock(node)
        self._finish(node)

    def play_sound(self, node, sound):
        self.lock(node)
        self._finish(node)

    def play_sound_file(self, node, filepath):
        self.lock(node)
        self._finish(node)

    def play_note(self, node, pitch, duration):
        self.lock(node)
        self._finish(node)


class _BackendKickActuator(_BackendActuator):
    def __init__(self, robot):
        super().__init__(robot, "kick")

    def kick(self, node, kicktype):
        self.lock(node)
        node.complete()

    def place(self, node):
        self.lock(node)
        node.complete()


class _BackendLEDsActuator(_BackendActuator):
    NUM_LEDS = 6

    def __init__(self, robot):
        super().__init__(robot, "leds")

    def set_light_color(self, node, *args):
        self.lock(node)


class _BackendDisplayActuator(_BackendActuator):
    def __init__(self, robot):
        super().__init__(robot, "display")

    def show_emoji(self, node, emoji, direction=vex.EmojiLookType.LOOK_FORWARD):
        self.lock(node)

    def hide_emoji(self, node):
        self.lock(node)


class _BackendStatusThread:
    def __init__(self, status):
        self.current_status = {"robot": status}
        self.callback = None


class _BackendImageThread:
    def __init__(self):
        self.callback = None
        self.image_list = []
        self._next_image_index = 0

    def stop_stream(self):
        return

    def start_stream(self):
        return


class _BackendInertial:
    def __init__(self):
        self._heading = 0.0
        self._pitch = 0.0
        self._roll = 0.0
        self._yaw = 0.0

    def calibrate(self):
        return

    def set_heading(self, heading):
        self._heading = float(heading)

    def get_heading(self):
        return float(self._heading)

    def get_pitch(self):
        return float(self._pitch)

    def get_roll(self):
        return float(self._roll)

    def get_yaw(self):
        return float(self._yaw)


class _BackendSound:
    def __init__(self):
        self._active = False

    def is_active(self):
        return self._active

    def play(self, sound, volume):
        self._active = False

    def play_local_file(self, filepath, volume):
        self._active = False

    def play_note(self, pitch, duration, volume):
        self._active = False


class _BackendLED:
    def on(self, *args):
        return


class _BackendKicker:
    def kick(self, kicktype):
        return

    def place(self):
        return


class _BackendScreen:
    def show_emoji(self, emoji, direction):
        return

    def hide_emoji(self):
        return


class _BackendVision:
    def get_camera_image(self):
        return

    def tag_detection(self, enabled):
        return


class BackendRobot0:
    def __init__(self):
        self._x = 0.0
        self._y = 0.0
        self._stopped = True

        self.inertial = _BackendInertial()
        self.sound = _BackendSound()
        self.led = _BackendLED()
        self.kicker = _BackendKicker()
        self.screen = _BackendScreen()
        self.vision = _BackendVision()

        self.status = {
            "battery": 100,
            "touch_flags": "0x00",
            "touch_x": 0,
            "touch_y": 0,
            "gyro_rate": {"x": "0", "y": "0", "z": "0"},
            "pitch": "0",
            "roll": "0",
            "aivision": {"objects": {"items": []}},
        }
        self._ws_status_thread = _BackendStatusThread(self.status)
        self._ws_img_thread = _BackendImageThread()

    def set_xy_position(self, x, y):
        self._x = float(x)
        self._y = float(y)

    def get_x_position(self):
        return float(self._x)

    def get_y_position(self):
        return float(self._y)

    def get_battery_capacity(self):
        return int(self.status.get("battery", 100))

    def is_stopped(self):
        return bool(self._stopped)

    def stop_all_movement(self):
        self._stopped = True

    def stop_all_motion(self):
        self.stop_all_movement()

    def turn_for(self, turntype, angle_degrees, turn_speed, units, wait):
        delta = float(angle_degrees) if turntype == vex.TurnType.LEFT else -float(angle_degrees)
        self.inertial._heading = (self.inertial._heading + delta) % 360
        self._stopped = True

    def move_for(self, distance_mm, angle_deg, drive_speed, units, wait):
        self._stopped = True

    def move_at(self, angle_deg, drive_speed, units):
        self._stopped = False

    def move_with_vectors(self, xvel, yvel, rvel):
        self._stopped = False

    def spin_wheels(self, left_vel, right_vel, back_vel):
        self._stopped = False


class BackendOnlyRobot:
    """
    Hardware-free robot implementation for GPT/FSM backend testing.
    """
    def __init__(self, loop=None, launch_speech_listener=False):
        self.loop = loop or asyncio.get_event_loop()
        self.robot0 = BackendRobot0()
        self.robot0.inertial.calibrate()
        self.robot0.inertial.set_heading(0)
        self.robot0.set_xy_position(0, 0)

        self.sound_volume = 100
        self.pose = PoseEstimate(0, 0, 0, 0)
        self.holding = None
        self.last_held_time = 0

        self.camera = Camera()
        self.kine = AIMKinematics(self)
        self.world_map = WorldMap(self)
        self.worldmap_viewer = None
        self.particle_filter = SLAMParticleFilter(self)
        self.particle_viewer = None
        self.rrt = RRT(self)
        self.path_planner = PathPlanner(self)
        self.path_viewer = None
        self.aruco_detector = None

        acts = [
            _BackendDriveActuator(self),
            _BackendSoundActuator(self),
            _BackendKickActuator(self),
            _BackendLEDsActuator(self),
            _BackendDisplayActuator(self),
        ]
        self.actuators = {act.name: act for act in acts}

        self.erouter = EventRouter(self)
        self.erouter.start()

        self.cam_viewer = None
        self.touch = "0x00"
        self.flask_thread = None
        self.openai_client = OpenAIClient(self)
        self.camera_image = np.zeros(
            (self.camera.resolution[1], self.camera.resolution[0], 3),
            dtype=np.uint8,
        )
        self.frame_count = 0
        self.moving_frame = 0
        self.status = self.robot0.status
        self.battery_percentage = self.status["battery"]
        self.speech_listener = _BackendSpeechListener()

    def status_update(self):
        self.status["battery"] = self.robot0.get_battery_capacity()
        self.battery_percentage = self.status["battery"]

    def set_sound_volume(self, volume):
        if isinstance(volume, int) and 0 <= volume <= 100:
            self.sound_volume = volume
        else:
            raise ValueError(f"Volume must be an integer from 0 to 100, not {volume!r}")

    def set_pose(self, x, y, z, theta, reset_particles=True):
        self.pose = PoseEstimate(x, y, z, theta)
        x0, y0, heading0 = -y, x, (360 - theta * 180 / math.pi)
        self.robot0.set_xy_position(x0, y0)
        self.robot0.inertial.set_heading(heading0)
        if self.particle_filter and reset_particles:
            self.particle_filter.set_pose(x, y, theta)

    def abort_all_actions(self):
        self.robot0.stop_all_movement()
        self.clear_actuators()

    def update_actuators(self):
        for act in self.actuators.values():
            act.status_update()

    def clear_actuators(self):
        for act in self.actuators.values():
            act.clear()

    def restart_img_thread(self):
        return

    def is_picked_up(self):
        return False

    def is_moving(self):
        return not self.robot0.is_stopped()

    def ask_gpt(self, query_text):
        self.openai_client.query(query_text)

    def gpt_note_for_later(self, text):
        self.openai_client.note_for_later(text)

    def send_gpt_camera(self, instruction=None):
        self.openai_client.send_camera_image(instruction=instruction)

    def ask_gpt_camera(self, query_text):
        self.openai_client.camera_query(query_text)

    def gpt_oneshot(self, query_text, image=None):
        self.openai_client.oneshot_query(query_text, image)

    def show_pose(self):
        heading = self.robot0.inertial.get_heading()
        print(
            f"Odometry:  {self.robot0.get_y_position():.1f}, {-self.robot0.get_x_position():.1f} "
            f"heading {-heading:.1f} deg."
        )
        print()

    def print_raw_odometry(self):
        print(
            f"x={self.robot0.get_x_position()} y={self.robot0.get_y_position()} "
            f"hdg={self.robot0.inertial.get_heading()}"
        )


class SimRobot():
    def __init__(self, run_in_cloud=False):
        robot = self
        robot.use_shared_map = False
        robot.particle_viewer = None
        robot.path_viewer = None
        robot.path_planner = PathPlanner(robot)
        robot.robot0 = SimRobot0()

        robot.pose = Pose(0, 0, 0, 0)
        robot.holding = None

        if not run_in_cloud:
            robot.loop = asyncio.get_event_loop()
            robot.erouter = EventRouter(robot)

        robot.world_map = WorldMap(robot)
        robot.world_map.wall_marker_dict = dict()
        robot.particle_filter = SLAMParticleFilter(robot)
        robot.kine = AIMKinematics(robot)
        robot.rrt = RRT(robot)
