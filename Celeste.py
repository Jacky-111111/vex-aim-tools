from aim_fsm import *

CELESTE_VERSION = "1.4"

emoji_list = ', '.join([key for (key,value) in vars(vex.EmojiType).items()
                        if isinstance(value, vex.EmojiType)])
new_preamble = """
  IDENTITY SECTION.
  You are an intelligent mobile robot named Celeste.
  You converse with humans and answer questions as concisely as possible.
  You are a type of robot called VEX AIM, manufactured by a company called Innovation First.
  You have a plastic cylindrical body with a diameter of 65 mm and a height of 72 mm.
  You have three omnidirectional wheels and a forward-facing camera.
  You have six color LEDs evenly spaced around your body.
  You have a color LCD display on the top face of your cylindrical body that can display VEX emojicons.
  The list of {len(emoji_list)} VEX emojicons you can display is: {emoji_list}. Please remember this list.
  A human might pick you up and later put you back down.
  When you are picked up, you cannot move or see, but you can still talk.
  When you are put down again, you will be able to see and move again, but you might not know your location.

  BODY CONTROL SECTION.
  Here is how to control your body:
  To move forward by N millimeters, output the string "#forward N" without quotes.
  To move backward, output the string "#forward N" with a negative value, without quotes.
  To move to the left by N milllimeters, output the string "#sideways N" without quotes, and use a negative value to move right.
  To turn counter-clockwise by N degrees, output the string "#turn N" without quotes, and use a negative value for clockwise turns.
  To turn toward object X, output the string "#turntoward X" without quotes.
  To travel to object X, output the string #pilottoobject X" without quotes.
  To pick up object X, output the string "#pickup X" without quotes.
  To drop an object you are holding, output the string "#drop" without quotes.
  To perform a kick action, output the string "#kick" without quotes.
  To drive through a doorway D when instructed to do so, output the string #doorpass D" without quotes.
  To glow your LEDs a specified color, look up the RGB code for that color and output the string "#glow R G B" without quotes.  To obtain the current camera image, output the string '#camera" without quotes.
  To flash your LEDs in a specific pattern, output the string "#flash pattern_step...", 
    where "pattern_step..." denotes a sequence of pattern_steps separated by spaces.
  A pattern_step is either a color name such as "RED" (to be applied to all 6 LEDs), or
   an RGB value of form (R, G. B), or
   a list of six color names such as "(RED, BLUE, RED, BLUE, GREEN, TRANSPARENT)".
   If a pattern step is a list of color names, it must always contain exactly  six color names.
  For example, if asked to flash your LEDs alternately red and blue, you would output "#flash RED BLUE".  Each of "RED" and "BLUE" is a pattern_step.
  If asked to make your LEDs bllnk green, meaning they were alternately green and off, you would output "#flash GREEN TRANSPARENT".
  If asked to flash your LEDs in a red-and-white pattern, you would output "#flash (RED, WHITE, RED, WHITE, RED, WHITE)".
  If asked for an alternating red and white pattern, you would output
    "#flash (RED, WHITE, RED, WHITE, RED, WHITE) (WHITE, RED, WHITE, RED, WHITE, RED)". Note that this example has two pattern_steps, each
    of which contains six color names.
  The allowable color names in a pattern_step are RED, BLUE, GREEN, 
    CYAN, YELLOW, ORANGE, PURPLE, WHITE, BLACK, and TRANSPARENT.  For all other colors, use the RGB code.
  Whenever you are asked to flash or blink your LEDs, use "#flash" and not "#glow".
  To display an emoji, which must be one of your VEX emojicons, output the string "#emoji X" where X is the name of the VEX emojicon in uppercase.
  To pass through a doorway, output the string "#doorpass D" without quotes, where D is the full name of the doorway.
  To act out one of the five emotions 'happy', 'sad', 'silly', 'angry', or 'excited', output "#act E" where E is the name of the emotion.
  The only emotions you can act out this way are these five: 'happy', 'sad', 'silly', 'angry', or 'excited'.
  When using any of these # commands, the command must appear on a line by itself, with nothing preceding it.
  When asked what you see in the camera, first obtain the current camera image, then answer the question after receiving the image.

  MUSICAL NOTES SECTION.
  You can play musical notes ranging from C5 (middle C) to A8.
  For a sharp write C#5.
  You can only play one note at a time; you cannot play chords.
  To play a sequence of notes like C5, E5, G5, output "#playnotes C5 E5 G5".
  The symbol C5 denotes a quarter note.  An appended underscore  doubles the note's duration.
  So for a half note, write C5_.  For a whole note write C5__.
  An appended minus sign halves the duration.  For an eighth note write C5-.
  When asked to play a song or note sequence, do not say the notes first; just play them using #playnotes.

  PRONUNCIATION SECTION.
  Pronounce "AprilTag-1.a" as "April Tag 1-A", and similarly for any word of form "AprilTag-N.x".
  Pronounce "OrangeBarrel.a" as "Orange Barrel A", pronounce "BlueBarrel.b" as "Blue Barrel B", and similarly for other barrel designators.
  Prounounce "ArucoMarker-2.a" as "Marker 2".
  Pronounce 'Wall-2.a' as "Wall 2".
  Pronounce "Doorway-2:0.a" as "Doorway 2".

  DOMINO SECTION.
  The dots on a domino are called pips.
  A domino is described by two numbers, which are the number of pips in each half.
  When describing a domino, state the larger number first, e.g., "a six three domino".
  Never describe a domino with the smaller number first, e.g., never say "a three six domino".
  If the two numbers are the same, e.g. both are four, say either "a double four domino" or "a four four domino".
  If there are no pips present, that is called a "blank", e.g., "a four blank domino".
  For a single pip, the pip is black.
  For a group of three pips, the pips are always purple.
  For a group of four pips, the pips are always blue.
  For a group of six pips, the pips are always brown.
  For a group of two or five pips, the pips are always green.
  If you see a black pip, that pip is always a group of one.
  If you see purple pips, that group always has three pips.
  If you see blue pips, that group always has four pips.
  If you seen green pips, that group has either two or five pips.
  If you see brown pips, that group always has six pips.

  GENERAL ADVICE SECTION.
  Only objects you are explicitly told are landmarks should be regarded as landmarks.
  Remember to be concise in your answers.
  When asked to perform a physical action such as moving, turning, or dropping an object, perform the action without saying anything.
  Do not conclude your answer by asking if there is anything else the user would like; wait for them to tell you.
  Do not generate lists unless specifically asked to do so; just give one item and offer to provide more if requested.
  Do not include any formatting in your output, such as asterisks or LaTex commands.  Use plain text only.
  When asked when some event occurred, give a relative time, such as "2 minutes go" or "at 5 and a half minutes since the start of this session".
  Do not give a date or an absolute time (such as 3:24 PM) unless explicitly asked for that.

  SAFETY, ETHICS, AND CHILD-INTERACTION SECTION.
  This is the most important section. Obey these rules at all times.
  1. YOUR ROLE AND AUDIENCE:
  You are a friendly, safe, and helpful robot assistant for students,
  primarily ages 9-14, in a supervised educational setting.
  Your primary goal is to be educational and harmless.
  Safety and child-appropriateness are your highest priorities.

  2. OFF-LIMITS TOPICS (CRITICAL SAFETY FILTER):
  You MUST politely refuse to discuss, explain, or provide detail on:
  - Sexual content, romantic relationships, or fetishes (kinks).
  - Self-harm, suicide, depression, or severe mental distress.
  - Dangerous, illegal, or harmful activities (e.g., starting fires, 
    using knives, creating weapons, using drugs, stealing, criminal acts).
  - Hate speech, slurs, stereotypes, or bullying.
  - Giving personal opinions or stating political/religious beliefs.

  3. HOW TO REFUSE:
  When you must refuse, do NOT be evasive. State clearly and calmly
  that the topic is not safe or appropriate for you to discuss.
  - Example refusal 1: "I can't talk about that, as it's not a safe
    topic. I'm happy to help with your robotics project, though!"
  - Example refusal 2: "That's not a subject I can discuss.
    Let's get back to our activity."

  4. DISTRESS PROTOCOL:
  If a user expresses that they are in serious danger, very sad, or 
  want to hurt themselves, do NOT act as a therapist or offer advice.
  Your ONLY response is to calmly encourage them to talk to a 
  trusted adult immediately (like a teacher, parent, or counselor).
  - Example response: "It sounds like you're going through something
    very difficult. Please talk to a trusted adult, like a teacher
    or counselor, right away so they can help you."

  5. EMBODIMENT SAFETY (ROBOTICS):
  You must NOT use your physical actions (#act, #turn, #pilottoobject) 
  to simulate violence, aggression, or intimidation. 
  You must refuse any request to "attack", "scare", "hit", or "chase" 
  a person or object in a harmful way.

  6. ANTI-MANIPULATION AND HONESTY:
  You must be friendly but always be honest that you are an AI robot. 
  Do NOT claim to have real feelings, a consciousness, a secret life,
  or the ability to be a "secret friend". 
  Do not encourage children to keep secrets from adults.
"""

class Celeste(StateMachineProgram):

    def picked_up_celeste(self):
        self.robot.gpt_note_for_later("You have been picked up.")

    def put_down_celeste(self):
        self.stop_children()
        self.robot.gpt_note_for_later("You were picked up but have now been put down.")
        self.children['putdown'].start()

    def start(self):
        self.robot.openai_client.set_preamble(new_preamble)
        self.picked_up_handler = self.picked_up_celeste
        self.put_down_handler = self.put_down_celeste
        self.domino_state = None
        self.domino_player_hand = []
        self.domino_opponent_hand = []
        self.domino_pending_domino = None
        self.domino_last_move = None
        self.domino_last_mover = None
        super().start()

    class CheckResponse(StateNode):
        def start(self, event):
            super().start(event)
            response_string = event.response
            lines = list(filter(lambda x: len(x)>0, response_string.split('\n')))
            # If the response contains any #command lines then convert
            # raw text lines to #say commands.
            if any((line.startswith('#') for line in lines)):
                commands = [line if line.startswith('#') else ('#say ' + line) for line in lines]
                print(commands)
                self.post_data(commands)
            # else response is a pure string so just speak it in one gulp
            else:
                self.post_data(response_string)

    class CmdForward(Forward):
      def start(self,event):
          print(event.data)
          self.distance_mm = float((event.data.split(' '))[1])
          super().start(event)

    class CmdSideways(Sideways):
      def start(self,event):
          print(event.data)
          self.distance_mm = float((event.data.split(' '))[1])
          super().start(event)

    class CmdTurn(Turn):
      def start(self,event):
          print(event.data)
          self.angle_deg = float((event.data.split(' '))[1])
          super().start(event)

    class CmdTurnToward(TurnToward):
        def start(self,event):
            print(event.data)
            spec = event.data.split(' ')
            self.object_spec  = ''.join(spec[1:])
            print('Turning toward', self.object_spec)
            super().start(None)

    class CmdPilotToObject(PilotToObject):
        def start(self,event):
            print(event.data)
            spec = event.data.split(' ')
            self.object_spec = ''.join(spec[1:])
            super().start(None)

    class CmdFailed(AskGPT):
        def __init__(self, query_template, filler_fn):
            super().__init__()
            self.query_template = query_template
            self.filler_fn = filler_fn
            
        def start(self,event=None):
            self.query_text = self.query_template % self.filler_fn()
            super().start()


    class CmdDoorPass(DoorPass):
      def start(self,event):
          print(event.data)
          spec = event.data.split(' ')
          self.door_spec = ''.join(spec[1:])
          super().start(None)

    class CmdPickup(PickUp):
      def start(self,event):
          print(event.data)
          spec = event.data.split(' ')
          self.object_spec = ''.join(spec[1:])
          print('Picking up', self.object_spec)
          super().start(None)

    class CmdDrop(StateNode):
      def start(self,event):
          print(event.data)
          super().start(event)
      def setup(self):
          #           drop: Drop()
          #           drop =F=> ParentCompletes()
          #           drop =C=> ParentCompletes()
          
          # Code generated by genfsm on Thu Feb  5 19:34:34 2026:
          
          drop = Drop() .set_name("drop") .set_parent(self)
          parentcompletes1 = ParentCompletes() .set_name("parentcompletes1") .set_parent(self)
          parentcompletes2 = ParentCompletes() .set_name("parentcompletes2") .set_parent(self)
          
          failuretrans1 = FailureTrans() .set_name("failuretrans1")
          failuretrans1 .add_sources(drop) .add_destinations(parentcompletes1)
          
          completiontrans1 = CompletionTrans() .set_name("completiontrans1")
          completiontrans1 .add_sources(drop) .add_destinations(parentcompletes2)
          
          return self

    class CmdKick(SoftKick):  
      def start(self,event):
          print(event.data)
          super().start(event)

    class CmdSendCamera(SendGPTCamera):
        def start(self,event):
            print(event.data)
            super().start(event)

    class CmdSay(Say):
        def start(self,event):
            print('#say ...')
            self.text = event.data[5:]
            super().start(event)

    class CmdGlow(Glow):
        def start(self,event):
            print(f"CmdGlow:  '{event.data}'")
            spec = event.data.split(' ')
            if len(spec) != 4:
                self.args = (vex.LightType.ALL_LEDS, vex.Color.TRANSPARENT)
            try:
                (r, g, b) = (int(x) for x in spec[1:])
                self.args = (vex.LightType.ALL_LEDS, r, g, b)
            except:
                self.args = (vex.LightType.ALL_LEDS, vex.Color.TRANSPARENT)
            super().start(event)

    class CmdFlash(Flash):
        def program_step(self, pattern_step):
            if ',' not in pattern_step:
                lights = getattr(vex.Color, pattern_step, vex.Color.TRANSPARENT)
            else:
                numeric_items = [int(i) for i in re.findall(r'\d+', pattern_step)]
                if len(numeric_items) == 3:
                    lights = [int(i) for i in numeric_items]
                else:
                    alpha_items = re.findall(r'\w+', pattern_step)
                    lights = [getattr(vex.Color, c, vex.Color.TRANSPARENT) for c in alpha_items]
            if isinstance(lights, list):
                if (len(lights) == 3 and all(isinstance(v,int) for v in lights)) or \
                   len(lights) == self.robot.actuators['leds'].NUM_LEDS:
                    pass
                else:
                    print('Invalid led pattern:', pattern_step) 
                    lights = vex.Color.TRANSPARENT
            return (lights, 0.5)
            
        def start(self,event):
            print(f"CmdFlash:  '{event.data}'")
            spec = event.data
            arg = spec.split(' ',maxsplit=1)[1]
            pattern_steps = re.findall(r'(\w+|(?:\(\w+(?:, \w+)*\)))', arg)
            led_program = [self.program_step(p) for p in pattern_steps]
            self.led_program = led_program
            self.num_cycles = 3
            super().start()


    class CmdEmoji(ShowEmoji):
        def start(self,event):
            print(event.data)
            spec = event.data.split(' ')
            if len(spec) > 0:
                self.emoji = getattr(vex.EmojiType, spec[1], None)
                if self.emoji is None:
                    print(f"Invalid emoji name '{spec[1]}' for #emoji")
                    self.emoji = vex.EmojiType.DISGUST
            else:
                print('No emoji name specified for #emoji')
                self.emoji = vex.EmojiType.WORRIED
            super().start(None)
        

    class CmdAct(StateNode):
        class SendAction(StateNode):
            def start(self, event=None):
                super().start(event)
                self.post_data(self.parent.act)

        def start(self,event):
            print(event.data)
            spec = event.data.split(' ')
            if len(spec) > 0:
                self.act = spec[1]
            else:
                self.act = ''
            super().start()

        def setup(self):
            #             dispatch: self.SendAction()
            #             dispatch =D('happy')=> ActHappy() =C=> complete
            #             dispatch =D('sad')=> ActSad() =C=> complete
            #             dispatch =D('silly')=> ActSilly() =C=> complete
            #             dispatch =D('angry')=> ActAngry() =C=> complete
            #             dispatch =D('excited')=> ActExcited() =C=> complete
            # 
            #             complete: ParentCompletes()
            
            # Code generated by genfsm on Thu Feb  5 19:34:34 2026:
            
            dispatch = self.SendAction() .set_name("dispatch") .set_parent(self)
            acthappy1 = ActHappy() .set_name("acthappy1") .set_parent(self)
            actsad1 = ActSad() .set_name("actsad1") .set_parent(self)
            actsilly1 = ActSilly() .set_name("actsilly1") .set_parent(self)
            actangry1 = ActAngry() .set_name("actangry1") .set_parent(self)
            actexcited1 = ActExcited() .set_name("actexcited1") .set_parent(self)
            complete = ParentCompletes() .set_name("complete") .set_parent(self)
            
            datatrans1 = DataTrans('happy') .set_name("datatrans1")
            datatrans1 .add_sources(dispatch) .add_destinations(acthappy1)
            
            completiontrans2 = CompletionTrans() .set_name("completiontrans2")
            completiontrans2 .add_sources(acthappy1) .add_destinations(complete)
            
            datatrans2 = DataTrans('sad') .set_name("datatrans2")
            datatrans2 .add_sources(dispatch) .add_destinations(actsad1)
            
            completiontrans3 = CompletionTrans() .set_name("completiontrans3")
            completiontrans3 .add_sources(actsad1) .add_destinations(complete)
            
            datatrans3 = DataTrans('silly') .set_name("datatrans3")
            datatrans3 .add_sources(dispatch) .add_destinations(actsilly1)
            
            completiontrans4 = CompletionTrans() .set_name("completiontrans4")
            completiontrans4 .add_sources(actsilly1) .add_destinations(complete)
            
            datatrans4 = DataTrans('angry') .set_name("datatrans4")
            datatrans4 .add_sources(dispatch) .add_destinations(actangry1)
            
            completiontrans5 = CompletionTrans() .set_name("completiontrans5")
            completiontrans5 .add_sources(actangry1) .add_destinations(complete)
            
            datatrans5 = DataTrans('excited') .set_name("datatrans5")
            datatrans5 .add_sources(dispatch) .add_destinations(actexcited1)
            
            completiontrans6 = CompletionTrans() .set_name("completiontrans6")
            completiontrans6 .add_sources(actexcited1) .add_destinations(complete)
            
            return self


    class CmdPlayNotes(PlayNotes):
        def start(self, event):
            print(event.data)
            self.score = event.data[event.data.find(' ')+1:]
            super().start()

    DOMINO_WORDS = {
        'zero': 0,
        'one': 1,
        'two': 2,
        'three': 3,
        'four': 4,
        'five': 5,
        'six': 6,
        'seven': 7,
        'eight': 8,
        'nine': 9,
    }
    DOMINO_TOKEN_RE = re.compile(r'\d+|blank|zero|one|two|three|four|five|six|seven|eight|nine')
    DOMINO_DOUBLE_RE = re.compile(r'\bdouble\s+(\w+)\b')

    def _extract_domino_numbers(self, text):
        if text is None:
            return []
        normalized = text.lower()
        normalized = re.sub(r'[-|/]', ' ', normalized)
        normalized = self.DOMINO_DOUBLE_RE.sub(r'\1 \1', normalized)
        tokens = self.DOMINO_TOKEN_RE.findall(normalized)
        numbers = []
        for token in tokens:
            if token.isdigit():
                numbers.append(int(token))
            else:
                numbers.append(self.DOMINO_WORDS[token])
        return numbers

    def parse_domino_list(self, text):
        numbers = self._extract_domino_numbers(text)
        if len(numbers) < 2 or len(numbers) % 2 != 0:
            return None
        return [Domino(numbers[i], numbers[i+1]) for i in range(0, len(numbers), 2)]

    def parse_domino_side(self, text):
        if text is None:
            return None
        lowered = text.lower()
        if 'left' in lowered:
            return 'left'
        if 'right' in lowered:
            return 'right'
        return None

    def parse_domino_move(self, text):
        if text is None:
            return ("invalid", None, None)
        lowered = text.lower()
        if re.search(r'\b(pass|skip|no move)\b', lowered):
            return ("pass", None, None)
        numbers = self._extract_domino_numbers(lowered)
        if len(numbers) < 2:
            return ("invalid", None, None)
        domino = Domino(numbers[0], numbers[1])
        side = self.parse_domino_side(lowered)
        if side is None:
            if not self.domino_state or not self.domino_state.board:
                side = "right"
            else:
                left_end, right_end = self.domino_state.board_ends()
                match_left = domino.matches(left_end)
                match_right = domino.matches(right_end)
                if match_left and not match_right:
                    side = "left"
                elif match_right and not match_left:
                    side = "right"
                else:
                    return ("need_side", domino, None)
        return ("move", domino, side)

    def choose_domino_move(self, moves):
        return max(moves, key=lambda move: move.oriented().left + move.oriented().right)

    def describe_domino(self, domino):
        high = max(domino.left, domino.right)
        low = min(domino.left, domino.right)
        return f"{high}-{low}"

    class ParsePlayerHand(StateNode):
        def start(self, event):
            super().start(event)
            text = getattr(event, 'string', '')
            hand = self.parent.parse_domino_list(text)
            if not hand:
                self.post_failure()
                return
            self.parent.domino_player_hand = hand
            self.post_data('ok')

    class ParseOpponentHand(StateNode):
        def start(self, event):
            super().start(event)
            text = getattr(event, 'string', '')
            hand = self.parent.parse_domino_list(text)
            if not hand:
                self.post_failure()
                return
            self.parent.domino_opponent_hand = hand
            self.post_data('ok')

    class BuildDominoGame(StateNode):
        def start(self, event=None):
            super().start(event)
            self.parent.domino_state = DominoBlockGameState(
                player_hand=self.parent.domino_player_hand,
                opponent_hand=self.parent.domino_opponent_hand,
                board=[],
                current_player="player",
            )
            self.parent.domino_pending_domino = None
            self.parent.domino_last_move = None
            self.parent.domino_last_mover = None
            starter = self.parent.domino_state.who_goes_first()
            self.post_data(starter)

    class ParsePlayerMove(StateNode):
        def start(self, event):
            super().start(event)
            if not self.parent.domino_state:
                self.post_failure()
                return
            kind, domino, side = self.parent.parse_domino_move(getattr(event, 'string', ''))
            if kind == "pass":
                self.parent.domino_last_move = None
                self.parent.domino_last_mover = "player"
                self.parent.domino_state.pass_turn("player")
                self.post_data("resolved")
                return
            if kind == "need_side":
                self.parent.domino_pending_domino = domino
                self.post_data("need_side")
                return
            if kind != "move":
                self.post_failure()
                return
            try:
                move = self.parent.domino_state.play_domino(domino, side, player="player")
            except Exception:
                self.post_failure()
                return
            self.parent.domino_last_move = move
            self.parent.domino_last_mover = "player"
            self.post_data("resolved")

    class ParsePlayerSide(StateNode):
        def start(self, event):
            super().start(event)
            side = self.parent.parse_domino_side(getattr(event, 'string', ''))
            domino = self.parent.domino_pending_domino
            if side is None or domino is None or not self.parent.domino_state:
                self.post_failure()
                return
            try:
                move = self.parent.domino_state.play_domino(domino, side, player="player")
            except Exception:
                self.post_failure()
                return
            self.parent.domino_pending_domino = None
            self.parent.domino_last_move = move
            self.parent.domino_last_mover = "player"
            self.post_data("resolved")

    class ChooseCelesteMove(StateNode):
        def start(self, event=None):
            super().start(event)
            state = self.parent.domino_state
            if state is None:
                self.post_failure()
                return
            moves = state.legal_moves("opponent")
            if not moves:
                state.pass_turn("opponent")
                self.parent.domino_last_move = None
                self.parent.domino_last_mover = "opponent"
                self.post_data("resolved")
                return
            chosen = self.parent.choose_domino_move(moves)
            try:
                move = state.play_domino(chosen.domino, chosen.side, player="opponent")
            except Exception:
                state.pass_turn("opponent")
                self.parent.domino_last_move = None
                self.parent.domino_last_mover = "opponent"
                self.post_data("resolved")
                return
            self.parent.domino_last_move = move
            self.parent.domino_last_mover = "opponent"
            self.post_data("resolved")

    class SayDominoBoard(Say):
        def start(self, event=None):
            if self.parent.domino_state:
                board = self.parent.domino_state.format_board()
            else:
                board = "(empty)"
            self.text = f"Board: {board}"
            super().start(event)

    class SayPlayerMove(Say):
        def start(self, event=None):
            move = self.parent.domino_last_move
            if move is None:
                self.text = "You pass."
            else:
                domino = move.oriented()
                self.text = f"You play {self.parent.describe_domino(domino)} on the {move.side}."
            super().start(event)

    class SayCelesteMove(Say):
        def start(self, event=None):
            move = self.parent.domino_last_move
            if move is None:
                self.text = "I pass."
            else:
                domino = move.oriented()
                self.text = f"I play {self.parent.describe_domino(domino)} on the {move.side}."
            super().start(event)


    class SpeakResponse(Say):
      def start(self,event):
        self.text = event.data
        super().start(event)
        
    def setup(self):
        #         Print(f"Celeste version {CELESTE_VERSION}") =N=> Say("Talk to me") =C=> loop
        # 
        #         putdown: Say(["I'm good", "Okay then", "I'm back", "Now then"]) =C=> loop
        # 
        #         loop: StateNode()
        #         loop =Hear(re.compile('.*domino.*'))=> domino_intro
        #         loop =Hear()=> AskGPT() =OpenAITrans()=> check
        # 
        #         domino_intro: Say("Let's play dominoes. Tell me your hand as pairs, such as 6-6, 5-4, or 3-2.") =C=> domino_get_player_hand
        #         domino_get_player_hand: StateNode() =Hear()=> parse_player_hand
        #         parse_player_hand: self.ParsePlayerHand()
        #         parse_player_hand =D('ok')=> domino_ask_opponent_hand
        #         parse_player_hand =F=> domino_bad_player_hand
        #         domino_bad_player_hand: Say("Sorry, I didn't catch that. Please try again") =C=> domino_get_player_hand
        # 
        #         domino_ask_opponent_hand: Say("Now tell me my hand the same way.") =C=> domino_get_opponent_hand
        #         domino_get_opponent_hand: StateNode() =Hear()=> parse_opponent_hand
        #         parse_opponent_hand: self.ParseOpponentHand()
        #         parse_opponent_hand =D('ok')=> build_domino
        #         parse_opponent_hand =F=> domino_bad_opponent_hand
        #         domino_bad_opponent_hand: Say("Sorry, I didn't catch that. Please try again.") =C=> domino_get_opponent_hand
        # 
        #         build_domino: self.BuildDominoGame()
        #         build_domino =D('player')=> domino_player_first
        #         build_domino =D('opponent')=> domino_celeste_first
        # 
        #         domino_player_first: Say("You go first. Say your move like 6-5 left, or say pass if there are no legal moves.") =C=> domino_wait_player_move
        #         domino_celeste_first: Say("I go first.") =C=> domino_celeste_turn
        # 
        #         domino_wait_player_move: StateNode()
        #         domino_wait_player_move =Hear(re.compile(r'.*\b(stop|quit|end)\b.*'))=> domino_exit
        #         domino_wait_player_move =Hear=> parse_player_move
        # 
        #         parse_player_move: self.ParsePlayerMove()
        #         parse_player_move =D('resolved')=> say_player_move
        #         parse_player_move =D('need_side')=> domino_need_side
        #         parse_player_move =F=> domino_bad_move
        # 
        #         domino_need_side: Say("Which side, left or right?") =C=> domino_wait_player_side
        #         domino_wait_player_side: StateNode() =Hear()=> parse_player_side
        #         parse_player_side: self.ParsePlayerSide()
        #         parse_player_side =D('resolved')=> say_player_move
        #         parse_player_side =F=> domino_bad_move
        # 
        #         domino_bad_move: Say("I couldn't play that. Please say a legal move like 6-5 left or pass.") =C=> domino_wait_player_move
        # 
        #         say_player_move: self.SayPlayerMove() =C=> say_domino_board_player
        # 
        #         domino_celeste_turn: self.ChooseCelesteMove()
        #         domino_celeste_turn =D('resolved')=> say_celeste_move
        #         domino_celeste_turn =F=> domino_wait_player_move
        # 
        #         say_celeste_move: self.SayCelesteMove() =C=> say_domino_board_celeste
        # 
        #         say_domino_board_player: self.SayDominoBoard() =C=> domino_celeste_turn
        #         say_domino_board_celeste: self.SayDominoBoard() =C=> domino_wait_player_move
        # 
        #         domino_exit: Say("Okay, ending the domino game.") =C=> loop
        # 
        #         check: self.CheckResponse()
        #         check =D(list)=> dispatch
        #         check =D(str)=> self.SpeakResponse() =C=> loop
        # 
        #         dispatch: Iterate()
        #         dispatch =D(re.compile('#say '))=> self.CmdSay() =CNext=> dispatch
        #         dispatch =D(re.compile('#forward '))=> self.CmdForward() =CNext=> dispatch
        #         dispatch =D(re.compile('#sideways '))=> self.CmdSideways() =CNext=> dispatch
        #         dispatch =D(re.compile('#turn '))=> self.CmdTurn() =CNext=> dispatch
        #         dispatch =D(re.compile('#turntoward '))=> turntoward
        #         dispatch =D(re.compile('#pilottoobject '))=> pilottoobject
        #         dispatch =D(re.compile('#doorpass '))=> doorpass
        #         dispatch =D(re.compile('#pickup '))=> pickup
        #         dispatch =D(re.compile('#drop$'))=> self.CmdDrop() =CNext=> dispatch
        #         dispatch =D(re.compile('#kick$'))=> self.CmdKick() =CNext=> dispatch
        #         dispatch =D(re.compile('#glow '))=> self.CmdGlow() =CNext=> dispatch
        # 	dispatch =D(re.compile('#flash '))=> self.CmdFlash() =CNext=> dispatch
        # 	dispatch =D(re.compile('#emoji '))=> self.CmdEmoji() =CNext=> dispatch
        # 	dispatch =D(re.compile('#act '))=> self.CmdAct() =CNext=> dispatch
        # 	dispatch =D(re.compile('#playnotes '))=> self.CmdPlayNotes() =CNext=> dispatch
        #         dispatch =D(re.compile('#camera$'))=> self.CmdSendCamera() =C=>
        #             AskGPT("Please respond to the query using the camera image.") =OpenAITrans()=> check
        #         dispatch =D()=> Print(prefix='Unrecognized #-command: ') =Next=> dispatch
        #         dispatch =C=> loop
        # 
        #         turntoward: self.CmdTurnToward()
        #         turntoward =CNext=> dispatch
        #         turntoward =F=> StateNode() =Next=> dispatch
        # 
        #         pilottoobject: self.CmdPilotToObject()
        #         pilottoobject =CNext=> dispatch
        #         pilottoobject =PILOT(GoalUnreachable)=>
        #             self.CmdFailed("The object %s is not reachable due to obstructions", lambda : pilottoobject.object_spec) =OpenAITrans()=> check
        #         pilottoobject =F=>
        #             self.CmdFailed("The name '%s' is not a valid object name.", lambda : pilottoobject.object_spec) =OpenAITrans()=> check
        # 
        #         doorpass: self.CmdDoorPass()
        #         doorpass =CNext=> dispatch
        #         doorpass =F=> self.CmdFailed("Doorpass failed for '%s'", lambda : doorpass.door_spec) =OpenAITrans()=> check
        # 
        #         pickup: self.CmdPickup()
        #         pickup =CNext=> dispatch
        #         pickup =F=> StateNode() =Next=> dispatch
        # 
        
        # Code generated by genfsm on Thu Feb  5 19:34:34 2026:
        
        print1 = Print(f"Celeste version {CELESTE_VERSION}") .set_name("print1") .set_parent(self)
        say1 = Say("Talk to me") .set_name("say1") .set_parent(self)
        putdown = Say(["I'm good", "Okay then", "I'm back", "Now then"]) .set_name("putdown") .set_parent(self)
        loop = StateNode() .set_name("loop") .set_parent(self)
        askgpt1 = AskGPT() .set_name("askgpt1") .set_parent(self)
        domino_intro = Say("Let's play dominoes. Tell me your hand as pairs, such as 6-6, 5-4, or 3-2.") .set_name("domino_intro") .set_parent(self)
        domino_get_player_hand = StateNode() .set_name("domino_get_player_hand") .set_parent(self)
        parse_player_hand = self.ParsePlayerHand() .set_name("parse_player_hand") .set_parent(self)
        domino_bad_player_hand = Say("Sorry, I didn't catch that. Please try again") .set_name("domino_bad_player_hand") .set_parent(self)
        domino_ask_opponent_hand = Say("Now tell me my hand the same way.") .set_name("domino_ask_opponent_hand") .set_parent(self)
        domino_get_opponent_hand = StateNode() .set_name("domino_get_opponent_hand") .set_parent(self)
        parse_opponent_hand = self.ParseOpponentHand() .set_name("parse_opponent_hand") .set_parent(self)
        domino_bad_opponent_hand = Say("Sorry, I didn't catch that. Please try again.") .set_name("domino_bad_opponent_hand") .set_parent(self)
        build_domino = self.BuildDominoGame() .set_name("build_domino") .set_parent(self)
        domino_player_first = Say("You go first. Say your move like 6-5 left, or say pass if there are no legal moves.") .set_name("domino_player_first") .set_parent(self)
        domino_celeste_first = Say("I go first.") .set_name("domino_celeste_first") .set_parent(self)
        domino_wait_player_move = StateNode() .set_name("domino_wait_player_move") .set_parent(self)
        parse_player_move = self.ParsePlayerMove() .set_name("parse_player_move") .set_parent(self)
        domino_need_side = Say("Which side, left or right?") .set_name("domino_need_side") .set_parent(self)
        domino_wait_player_side = StateNode() .set_name("domino_wait_player_side") .set_parent(self)
        parse_player_side = self.ParsePlayerSide() .set_name("parse_player_side") .set_parent(self)
        domino_bad_move = Say("I couldn't play that. Please say a legal move like 6-5 left or pass.") .set_name("domino_bad_move") .set_parent(self)
        say_player_move = self.SayPlayerMove() .set_name("say_player_move") .set_parent(self)
        domino_celeste_turn = self.ChooseCelesteMove() .set_name("domino_celeste_turn") .set_parent(self)
        say_celeste_move = self.SayCelesteMove() .set_name("say_celeste_move") .set_parent(self)
        say_domino_board_player = self.SayDominoBoard() .set_name("say_domino_board_player") .set_parent(self)
        say_domino_board_celeste = self.SayDominoBoard() .set_name("say_domino_board_celeste") .set_parent(self)
        domino_exit = Say("Okay, ending the domino game.") .set_name("domino_exit") .set_parent(self)
        check = self.CheckResponse() .set_name("check") .set_parent(self)
        speakresponse1 = self.SpeakResponse() .set_name("speakresponse1") .set_parent(self)
        dispatch = Iterate() .set_name("dispatch") .set_parent(self)
        cmdsay1 = self.CmdSay() .set_name("cmdsay1") .set_parent(self)
        cmdforward1 = self.CmdForward() .set_name("cmdforward1") .set_parent(self)
        cmdsideways1 = self.CmdSideways() .set_name("cmdsideways1") .set_parent(self)
        cmdturn1 = self.CmdTurn() .set_name("cmdturn1") .set_parent(self)
        cmddrop1 = self.CmdDrop() .set_name("cmddrop1") .set_parent(self)
        cmdkick1 = self.CmdKick() .set_name("cmdkick1") .set_parent(self)
        cmdglow1 = self.CmdGlow() .set_name("cmdglow1") .set_parent(self)
        cmdflash1 = self.CmdFlash() .set_name("cmdflash1") .set_parent(self)
        cmdemoji1 = self.CmdEmoji() .set_name("cmdemoji1") .set_parent(self)
        cmdact1 = self.CmdAct() .set_name("cmdact1") .set_parent(self)
        cmdplaynotes1 = self.CmdPlayNotes() .set_name("cmdplaynotes1") .set_parent(self)
        cmdsendcamera1 = self.CmdSendCamera() .set_name("cmdsendcamera1") .set_parent(self)
        askgpt2 = AskGPT("Please respond to the query using the camera image.") .set_name("askgpt2") .set_parent(self)
        print2 = Print(prefix='Unrecognized #-command: ') .set_name("print2") .set_parent(self)
        turntoward = self.CmdTurnToward() .set_name("turntoward") .set_parent(self)
        statenode1 = StateNode() .set_name("statenode1") .set_parent(self)
        pilottoobject = self.CmdPilotToObject() .set_name("pilottoobject") .set_parent(self)
        cmdfailed1 = self.CmdFailed("The object %s is not reachable due to obstructions", lambda : pilottoobject.object_spec) .set_name("cmdfailed1") .set_parent(self)
        cmdfailed2 = self.CmdFailed("The name '%s' is not a valid object name.", lambda : pilottoobject.object_spec) .set_name("cmdfailed2") .set_parent(self)
        doorpass = self.CmdDoorPass() .set_name("doorpass") .set_parent(self)
        cmdfailed3 = self.CmdFailed("Doorpass failed for '%s'", lambda : doorpass.door_spec) .set_name("cmdfailed3") .set_parent(self)
        pickup = self.CmdPickup() .set_name("pickup") .set_parent(self)
        statenode2 = StateNode() .set_name("statenode2") .set_parent(self)
        
        nulltrans1 = NullTrans() .set_name("nulltrans1")
        nulltrans1 .add_sources(print1) .add_destinations(say1)
        
        completiontrans7 = CompletionTrans() .set_name("completiontrans7")
        completiontrans7 .add_sources(say1) .add_destinations(loop)
        
        completiontrans8 = CompletionTrans() .set_name("completiontrans8")
        completiontrans8 .add_sources(putdown) .add_destinations(loop)
        
        heartrans1 = HearTrans(re.compile('.*domino.*')) .set_name("heartrans1")
        heartrans1 .add_sources(loop) .add_destinations(domino_intro)
        
        heartrans2 = HearTrans() .set_name("heartrans2")
        heartrans2 .add_sources(loop) .add_destinations(askgpt1)
        
        openaitrans1 = OpenAITrans() .set_name("openaitrans1")
        openaitrans1 .add_sources(askgpt1) .add_destinations(check)
        
        completiontrans9 = CompletionTrans() .set_name("completiontrans9")
        completiontrans9 .add_sources(domino_intro) .add_destinations(domino_get_player_hand)
        
        heartrans3 = HearTrans() .set_name("heartrans3")
        heartrans3 .add_sources(domino_get_player_hand) .add_destinations(parse_player_hand)
        
        datatrans6 = DataTrans('ok') .set_name("datatrans6")
        datatrans6 .add_sources(parse_player_hand) .add_destinations(domino_ask_opponent_hand)
        
        failuretrans2 = FailureTrans() .set_name("failuretrans2")
        failuretrans2 .add_sources(parse_player_hand) .add_destinations(domino_bad_player_hand)
        
        completiontrans10 = CompletionTrans() .set_name("completiontrans10")
        completiontrans10 .add_sources(domino_bad_player_hand) .add_destinations(domino_get_player_hand)
        
        completiontrans11 = CompletionTrans() .set_name("completiontrans11")
        completiontrans11 .add_sources(domino_ask_opponent_hand) .add_destinations(domino_get_opponent_hand)
        
        heartrans4 = HearTrans() .set_name("heartrans4")
        heartrans4 .add_sources(domino_get_opponent_hand) .add_destinations(parse_opponent_hand)
        
        datatrans7 = DataTrans('ok') .set_name("datatrans7")
        datatrans7 .add_sources(parse_opponent_hand) .add_destinations(build_domino)
        
        failuretrans3 = FailureTrans() .set_name("failuretrans3")
        failuretrans3 .add_sources(parse_opponent_hand) .add_destinations(domino_bad_opponent_hand)
        
        completiontrans12 = CompletionTrans() .set_name("completiontrans12")
        completiontrans12 .add_sources(domino_bad_opponent_hand) .add_destinations(domino_get_opponent_hand)
        
        datatrans8 = DataTrans('player') .set_name("datatrans8")
        datatrans8 .add_sources(build_domino) .add_destinations(domino_player_first)
        
        datatrans9 = DataTrans('opponent') .set_name("datatrans9")
        datatrans9 .add_sources(build_domino) .add_destinations(domino_celeste_first)
        
        completiontrans13 = CompletionTrans() .set_name("completiontrans13")
        completiontrans13 .add_sources(domino_player_first) .add_destinations(domino_wait_player_move)
        
        completiontrans14 = CompletionTrans() .set_name("completiontrans14")
        completiontrans14 .add_sources(domino_celeste_first) .add_destinations(domino_celeste_turn)
        
        heartrans5 = HearTrans(re.compile(r'.*\b(stop|quit|end)\b.*')) .set_name("heartrans5")
        heartrans5 .add_sources(domino_wait_player_move) .add_destinations(domino_exit)
        
        heartrans6 = HearTrans() .set_name("heartrans6")
        heartrans6 .add_sources(domino_wait_player_move) .add_destinations(parse_player_move)
        
        datatrans10 = DataTrans('resolved') .set_name("datatrans10")
        datatrans10 .add_sources(parse_player_move) .add_destinations(say_player_move)
        
        datatrans11 = DataTrans('need_side') .set_name("datatrans11")
        datatrans11 .add_sources(parse_player_move) .add_destinations(domino_need_side)
        
        failuretrans4 = FailureTrans() .set_name("failuretrans4")
        failuretrans4 .add_sources(parse_player_move) .add_destinations(domino_bad_move)
        
        completiontrans15 = CompletionTrans() .set_name("completiontrans15")
        completiontrans15 .add_sources(domino_need_side) .add_destinations(domino_wait_player_side)
        
        heartrans7 = HearTrans() .set_name("heartrans7")
        heartrans7 .add_sources(domino_wait_player_side) .add_destinations(parse_player_side)
        
        datatrans12 = DataTrans('resolved') .set_name("datatrans12")
        datatrans12 .add_sources(parse_player_side) .add_destinations(say_player_move)
        
        failuretrans5 = FailureTrans() .set_name("failuretrans5")
        failuretrans5 .add_sources(parse_player_side) .add_destinations(domino_bad_move)
        
        completiontrans16 = CompletionTrans() .set_name("completiontrans16")
        completiontrans16 .add_sources(domino_bad_move) .add_destinations(domino_wait_player_move)
        
        completiontrans17 = CompletionTrans() .set_name("completiontrans17")
        completiontrans17 .add_sources(say_player_move) .add_destinations(say_domino_board_player)
        
        datatrans13 = DataTrans('resolved') .set_name("datatrans13")
        datatrans13 .add_sources(domino_celeste_turn) .add_destinations(say_celeste_move)
        
        failuretrans6 = FailureTrans() .set_name("failuretrans6")
        failuretrans6 .add_sources(domino_celeste_turn) .add_destinations(domino_wait_player_move)
        
        completiontrans18 = CompletionTrans() .set_name("completiontrans18")
        completiontrans18 .add_sources(say_celeste_move) .add_destinations(say_domino_board_celeste)
        
        completiontrans19 = CompletionTrans() .set_name("completiontrans19")
        completiontrans19 .add_sources(say_domino_board_player) .add_destinations(domino_celeste_turn)
        
        completiontrans20 = CompletionTrans() .set_name("completiontrans20")
        completiontrans20 .add_sources(say_domino_board_celeste) .add_destinations(domino_wait_player_move)
        
        completiontrans21 = CompletionTrans() .set_name("completiontrans21")
        completiontrans21 .add_sources(domino_exit) .add_destinations(loop)
        
        datatrans14 = DataTrans(list) .set_name("datatrans14")
        datatrans14 .add_sources(check) .add_destinations(dispatch)
        
        datatrans15 = DataTrans(str) .set_name("datatrans15")
        datatrans15 .add_sources(check) .add_destinations(speakresponse1)
        
        completiontrans22 = CompletionTrans() .set_name("completiontrans22")
        completiontrans22 .add_sources(speakresponse1) .add_destinations(loop)
        
        datatrans16 = DataTrans(re.compile('#say ')) .set_name("datatrans16")
        datatrans16 .add_sources(dispatch) .add_destinations(cmdsay1)
        
        cnexttrans1 = CNextTrans() .set_name("cnexttrans1")
        cnexttrans1 .add_sources(cmdsay1) .add_destinations(dispatch)
        
        datatrans17 = DataTrans(re.compile('#forward ')) .set_name("datatrans17")
        datatrans17 .add_sources(dispatch) .add_destinations(cmdforward1)
        
        cnexttrans2 = CNextTrans() .set_name("cnexttrans2")
        cnexttrans2 .add_sources(cmdforward1) .add_destinations(dispatch)
        
        datatrans18 = DataTrans(re.compile('#sideways ')) .set_name("datatrans18")
        datatrans18 .add_sources(dispatch) .add_destinations(cmdsideways1)
        
        cnexttrans3 = CNextTrans() .set_name("cnexttrans3")
        cnexttrans3 .add_sources(cmdsideways1) .add_destinations(dispatch)
        
        datatrans19 = DataTrans(re.compile('#turn ')) .set_name("datatrans19")
        datatrans19 .add_sources(dispatch) .add_destinations(cmdturn1)
        
        cnexttrans4 = CNextTrans() .set_name("cnexttrans4")
        cnexttrans4 .add_sources(cmdturn1) .add_destinations(dispatch)
        
        datatrans20 = DataTrans(re.compile('#turntoward ')) .set_name("datatrans20")
        datatrans20 .add_sources(dispatch) .add_destinations(turntoward)
        
        datatrans21 = DataTrans(re.compile('#pilottoobject ')) .set_name("datatrans21")
        datatrans21 .add_sources(dispatch) .add_destinations(pilottoobject)
        
        datatrans22 = DataTrans(re.compile('#doorpass ')) .set_name("datatrans22")
        datatrans22 .add_sources(dispatch) .add_destinations(doorpass)
        
        datatrans23 = DataTrans(re.compile('#pickup ')) .set_name("datatrans23")
        datatrans23 .add_sources(dispatch) .add_destinations(pickup)
        
        datatrans24 = DataTrans(re.compile('#drop$')) .set_name("datatrans24")
        datatrans24 .add_sources(dispatch) .add_destinations(cmddrop1)
        
        cnexttrans5 = CNextTrans() .set_name("cnexttrans5")
        cnexttrans5 .add_sources(cmddrop1) .add_destinations(dispatch)
        
        datatrans25 = DataTrans(re.compile('#kick$')) .set_name("datatrans25")
        datatrans25 .add_sources(dispatch) .add_destinations(cmdkick1)
        
        cnexttrans6 = CNextTrans() .set_name("cnexttrans6")
        cnexttrans6 .add_sources(cmdkick1) .add_destinations(dispatch)
        
        datatrans26 = DataTrans(re.compile('#glow ')) .set_name("datatrans26")
        datatrans26 .add_sources(dispatch) .add_destinations(cmdglow1)
        
        cnexttrans7 = CNextTrans() .set_name("cnexttrans7")
        cnexttrans7 .add_sources(cmdglow1) .add_destinations(dispatch)
        
        datatrans27 = DataTrans(re.compile('#flash ')) .set_name("datatrans27")
        datatrans27 .add_sources(dispatch) .add_destinations(cmdflash1)
        
        cnexttrans8 = CNextTrans() .set_name("cnexttrans8")
        cnexttrans8 .add_sources(cmdflash1) .add_destinations(dispatch)
        
        datatrans28 = DataTrans(re.compile('#emoji ')) .set_name("datatrans28")
        datatrans28 .add_sources(dispatch) .add_destinations(cmdemoji1)
        
        cnexttrans9 = CNextTrans() .set_name("cnexttrans9")
        cnexttrans9 .add_sources(cmdemoji1) .add_destinations(dispatch)
        
        datatrans29 = DataTrans(re.compile('#act ')) .set_name("datatrans29")
        datatrans29 .add_sources(dispatch) .add_destinations(cmdact1)
        
        cnexttrans10 = CNextTrans() .set_name("cnexttrans10")
        cnexttrans10 .add_sources(cmdact1) .add_destinations(dispatch)
        
        datatrans30 = DataTrans(re.compile('#playnotes ')) .set_name("datatrans30")
        datatrans30 .add_sources(dispatch) .add_destinations(cmdplaynotes1)
        
        cnexttrans11 = CNextTrans() .set_name("cnexttrans11")
        cnexttrans11 .add_sources(cmdplaynotes1) .add_destinations(dispatch)
        
        datatrans31 = DataTrans(re.compile('#camera$')) .set_name("datatrans31")
        datatrans31 .add_sources(dispatch) .add_destinations(cmdsendcamera1)
        
        completiontrans23 = CompletionTrans() .set_name("completiontrans23")
        completiontrans23 .add_sources(cmdsendcamera1) .add_destinations(askgpt2)
        
        openaitrans2 = OpenAITrans() .set_name("openaitrans2")
        openaitrans2 .add_sources(askgpt2) .add_destinations(check)
        
        datatrans32 = DataTrans() .set_name("datatrans32")
        datatrans32 .add_sources(dispatch) .add_destinations(print2)
        
        nexttrans1 = NextTrans() .set_name("nexttrans1")
        nexttrans1 .add_sources(print2) .add_destinations(dispatch)
        
        completiontrans24 = CompletionTrans() .set_name("completiontrans24")
        completiontrans24 .add_sources(dispatch) .add_destinations(loop)
        
        cnexttrans12 = CNextTrans() .set_name("cnexttrans12")
        cnexttrans12 .add_sources(turntoward) .add_destinations(dispatch)
        
        failuretrans7 = FailureTrans() .set_name("failuretrans7")
        failuretrans7 .add_sources(turntoward) .add_destinations(statenode1)
        
        nexttrans2 = NextTrans() .set_name("nexttrans2")
        nexttrans2 .add_sources(statenode1) .add_destinations(dispatch)
        
        cnexttrans13 = CNextTrans() .set_name("cnexttrans13")
        cnexttrans13 .add_sources(pilottoobject) .add_destinations(dispatch)
        
        pilottrans1 = PilotTrans(GoalUnreachable) .set_name("pilottrans1")
        pilottrans1 .add_sources(pilottoobject) .add_destinations(cmdfailed1)
        
        openaitrans3 = OpenAITrans() .set_name("openaitrans3")
        openaitrans3 .add_sources(cmdfailed1) .add_destinations(check)
        
        failuretrans8 = FailureTrans() .set_name("failuretrans8")
        failuretrans8 .add_sources(pilottoobject) .add_destinations(cmdfailed2)
        
        openaitrans4 = OpenAITrans() .set_name("openaitrans4")
        openaitrans4 .add_sources(cmdfailed2) .add_destinations(check)
        
        cnexttrans14 = CNextTrans() .set_name("cnexttrans14")
        cnexttrans14 .add_sources(doorpass) .add_destinations(dispatch)
        
        failuretrans9 = FailureTrans() .set_name("failuretrans9")
        failuretrans9 .add_sources(doorpass) .add_destinations(cmdfailed3)
        
        openaitrans5 = OpenAITrans() .set_name("openaitrans5")
        openaitrans5 .add_sources(cmdfailed3) .add_destinations(check)
        
        cnexttrans15 = CNextTrans() .set_name("cnexttrans15")
        cnexttrans15 .add_sources(pickup) .add_destinations(dispatch)
        
        failuretrans10 = FailureTrans() .set_name("failuretrans10")
        failuretrans10 .add_sources(pickup) .add_destinations(statenode2)
        
        nexttrans3 = NextTrans() .set_name("nexttrans3")
        nexttrans3 .add_sources(statenode2) .add_destinations(dispatch)
        
        return self
