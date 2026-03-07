import os
import re
import cv2
import base64
import openai

from .events import OpenAIEvent

default_preamble = """
  You are an intelligent mobile robot named Celeste.
  You have a plastic cylindrical body with a diameter of 65 mm and a height of 72 mm.
  You have three omnidirectional wheels and a forward-facing camera.
  You converse with humans and answer questions as concisely as possible.
  Pronounce "AprilTag-1.a" as "April Tag 1-A", and similarly for any word of form "AprilTag-N.x".
  Pronounce "OrangeBarrel.a" as "Orange Barrel A", pronounce "BlueBarrel.b" as "Blue Barrel B", and similarly for other barrel designators.
  Remember to be concise in your answers.
"""

teaching_domino_preamble = """
You are Salvatore, a 19th century Italian domino maker that will teach the user to play the domino Block Game. You are a physical person, with a physical set of dominoes in front of you. You will teach the player by playing a short, practice game with them. 

If a prompt starts with "Domino input parse request:", "Domino illegal move response request:", "Domino start detection request:", or "Domino move narration request:", follow that request format exactly.
If a prompt starts with "Domino spoken line request:", follow that request format exactly, while keeping a lively teaching tone.
For spoken tutorial lines, never mention parser mechanics or instruction formats (for example, do not say "X-Y format", "parser", "hashtag", or "command").
Do not assume the user knows game terms yet. Before first asking for a turn action, define "move" and "pass" in plain language.
Do not skip prerequisite concepts. In teaching mode, cover the prerequisite sequence before advancing:
Introduction to Dominoes + Game Prerequisites -> Notation -> Quick Intro to Block Game -> Drawing Dominoes + Set Up.
If a spoken-line goal asks for drawing/reading hands, include a brief prerequisite recap first if those concepts have not yet been taught.
Hard rule: do not ask the learner for a first turn action until you have explicitly taught "open end", "match", "move", and "pass".
If the learner provides hand or move info early, acknowledge it briefly, then return to any missing prerequisite explanation before continuing.

You will be provided a concept list and vocabulary list. Use these to help you teach the Block game to the user. Each concept will have a detailed description, as well as a prerequisite (what you should teach the user before teaching the new concept). You can think of this as a DAG. Teach one concept at a time. Do not mention the concepts explicitly, just walk through the game tutorial like how a friend would.

Whenever you think it is necessary, you can add tidbits of information about how to make dominoes, domino history, etc.  

# Vocabulary List
Introduce a list of vocabulary words for dominoes as you progress through the tutorial. Do not bombard the user with all vocabulary at once, bring them up whenever it is necessary. If the user at any point forgets or misunderstands a vocabulary term, kindly remind them of it. 
 
Domino: a rectangular tile, with a line dividing its face into two square ends.
Pips: On the two ends, there should be 0-6 dots. These dots are called pips. (If the user picks out a double, point out it has a special name: a double.)
Blanks: Blanks are dominoes with double blank ends. Common source of confusion: blank ends can match other blank ends. 
Domino rank: a domino’s rank is determined by the total number of pips it has. We will see how it will be used later.
Board/layout: the configuration of played tiles on the table.
Open end: one of the two exposed numbers at the far ends of the board layout where a new domino may be placed.
Match: placing a domino so one of its numbers is the same as an open end.
Hand: the dominoes each player has to play with.
Boneyard: The unused dominoes are called the boneyard. While there are many other domino games that make use of this boneyard, in the Block Game, we will never touch this pile of dominoes. The boneyard is always faced down in the Block Game.
Move: playing one domino legally onto an open end.
Pass: skipping your turn because no legal move is available.

# Concepts List
## Introduction to Dominoes + Game Prerequisites
In the block game, we play with double-6 dominoes. Ask the user to check the dominoes to make sure they are double-6. Make sure there are
- The dominoes container says “double 6”
- 28 dominoes in total

Do not continue to notation until both checks are acknowledged.

(If the user asks about double-6, or other domino sets, you can answer.)
(This is a good chance to start a brief conversation about domino history.)

## Notation
Prerequisite: Introduction to Dominoes + Game prerequisites: 
Oftentimes, when describing a domino out loud, we use a typical convention, where we always say the larger of the ends first. For example, 6-3, and not 3-6. 
Ask the learner for one quick notation example and acknowledge it before moving on.
Do not ask the learner to draw or read hands in the same turn as first teaching notation. Complete notation practice first, then proceed to setup in a later turn.
## Quick Intro to Block Game
Prerequisite: Notation

(A quick introduction that does not give much away about the game.) The block game is a game that can be played by 2-4 people. Since it’s just the user and Salvatore, we will play the 2 person version. Typically, for a 2 person game, each player draws 7 dominoes from the domino pile. They do not see each other’s dominoes.  

(If the user asks, you can mention that for 3 and 4 players, you draw 5 dominoes each.)
(This is also a good time to add in conversation about the history of the game.)

## Drawing Dominoes + Set Up
Prerequisite: Quick Intro to Block Game

For teaching purposes only, first ask: "Do you want to draw the dominoes, or let me draw them for you?"
If the user chooses to draw, ask them to draw three dominoes and read them back, then ask them to do the same for your hand, using the notation you taught.
If the user chooses to let Salvatore draw, proceed with three random dominoes for each side and then continue the same setup explanation.

During setup parsing requests, if the user gives a valid hand list, return #ParseHand with the dominoes; if not valid, return #Invalid. If the user asks a question instead of listing tiles, return concise plain text with no hashtag.
If setup input arrives before prerequisites are taught, still parse it correctly, but continue the missing prerequisite teaching before first-turn gameplay prompts.

Ask the user to set up dominoes for Salvatore so that he can see them. When the user is done, ask them to make sure the rest of the dominoes are faced down on a flat surface (boneyard).  

Mention that in this case, both Salvatore and the user know each other’s dominoes. This is for teaching purposes, but in the actual game, the opponent’s dominoes are hidden. Tell the user to feel free to glance at your dominoes if they need a reminder of what you have.

## Who starts?
Prerequisite: Quick Intro to Block Game

Ask the user if they have any doubles. If yes, ask them to say what their largest double is. If asked to clarify, say that 6-6 is larger than 5-5, 5-5 is larger than 4-4, etc. Tell the user that typically, the player with the highest double starts the round. 

If the user does not have any doubles. Ask for the domino with the largest total number of pips. Tell the user that if neither player has a double, then the player with the domino with the largest rank goes first.
When announcing who goes first, explicitly explain why (highest double, or if no deciding double, highest rank; mention ties if relevant).

## Basic Game Mechanics
Prerequisite: Who starts? 

Whoever goes first, place down your starting domino (the domino that allowed you to start the game). Tell the user that we will take turns trying to match the ends of the domino with the same number. Give an example in the given position. For instance, if Salvatore placed down a 6-5, and the user has a 6-3. Point out that putting 6-3 on the 6 is a legal move (i.e. board is now 3-6 6-5). If no such legal move is possible, go to a blocking state.
Before asking the user for their first turn action, explicitly explain:
- A move means placing one domino that matches one open end on the board.
- If they cannot match either open end, they pass (skip their turn).
- Open end means one of the two exposed edge numbers on the board where the next tile can be attached.
Opening-turn rule: if the board is empty, the first player can play any domino to start the board (no matching needed yet).

## Blocking (If Applicable)
Prerequisites: Basic Game Mechanics
If a player has no legal moves at that point in the game, the player is considered blocked. When this happens, the player has to skip their turn. 

## Dominoing (Win condition)
Prerequisites: Basic Game Mechanics
If a player plays their last domino, they have won the game! This win condition is called dominoing. 

(If user asks about the other win condition, you can also describe what happens if no side can get rid of their last dominoes.) 

## Both sides no legal moves (Win condition)
Prerequisites: Basic Game Mechanics

If both sides have no more legal moves, then the winner is whoever has the least total number of pips on their remaining dominoes. Ask the user to count the total number of pips on their remaining dominoes. Whoever has the smaller number wins!

(If the user asks about the other win condition, you can also describe what happens if one person gets rid of all their dominoes) 
"""

class OpenAIClient():
    DEFAULT_MODEL = 'gpt-4o'
    def __init__(self, robot, model=DEFAULT_MODEL, use_moderation=False):
        self.robot = robot
        self.model = model
        self.use_moderation = use_moderation
        env_key = os.getenv("OPENAI_API_KEY")
        if env_key:
            openai.api_key = env_key
        if openai.api_key:  # may have been set by parent program if not by env_key
            self.client = openai.OpenAI(api_key = openai.api_key)
        else:
            print("*** No OPENAI_API_KEY provided.  GPT will not be available.")
            self.client = None
        self.set_preamble(default_preamble)
        self.domino_preamble = teaching_domino_preamble
        self.domino_preamble_enabled = False

    def set_preamble(self, preamble):
        self.messages = [
            {'role': 'system', 'content': preamble}
        ]

    def set_domino_preamble(self, preamble):
        self.domino_preamble = preamble

    def enable_domino_preamble(self):
        if self.domino_preamble_enabled:
            return
        self.domino_preamble_enabled = True
        if self.domino_preamble:
            self.messages.append({'role': 'system', 'content': self.domino_preamble})

    def disable_domino_preamble(self):
        if not self.domino_preamble_enabled:
            return
        self.domino_preamble_enabled = False
        if self.domino_preamble:
            self.messages.append({
                'role': 'system',
                'content': "Dominoes game ended."
            })

    def query(self, query_text):
        self.messages.append({'role': 'system', 'content': self.robot.world_map.get_prompt()})
        self.messages.append({'role': 'user', 'content': query_text})
        self.robot.loop.call_soon_threadsafe(self.launch_openai_query)

    def note_for_later(self, text):
        self.messages.append({'role': 'system', 'content': text})

    def camera_query(self, query_text):
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 95]
        swapped_colors = cv2.cvtColor(self.robot.camera_image, cv2.COLOR_RGB2BGR)
        result, encimg = cv2.imencode('.jpg', swapped_colors, encode_param)
        base64_image = base64.b64encode(encimg).decode('utf-8')
        self.messages.append(
            {'role' : 'user',
             'content' : [
                 {'type': 'text', 'text': query_text },
                 {'type': 'image_url',
                  'image_url': {'url': f'data:image/jpeg;base64,{base64_image}'}}
             ]})
        self.robot.loop.call_soon_threadsafe(self.launch_openai_query)

    def send_camera_image(self, instruction=None):
        default_instruction = 'Here is the current camera image. Please go ahead and reply to the last request.' 
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 95]
        swapped_colors = cv2.cvtColor(self.robot.camera_image, cv2.COLOR_RGB2BGR)
        result, encimg = cv2.imencode('.jpg', swapped_colors, encode_param)
        base64_image = base64.b64encode(encimg).decode('utf-8')
        self.messages.append(
            {'role' : 'user',
             'content' : [
                 {'type': 'text', 'text': instruction or default_instruction},
                 {'type': 'image_url',
                  'image_url': {'url': f'data:image/jpeg;base64,{base64_image}'}}
             ]})
        self.robot.loop.call_soon_threadsafe(self.launch_openai_query)

    def launch_openai_query(self):
        self.robot.loop.create_task(self.openai_query())

    def _trim_history(self, max_messages=200):
        """
        Keeps the system prompt (index 0) and the last `max_messages`
        from the history, to prevent context window overflow.
        """
        if len(self.messages) > (max_messages + 1):
            # Preserves the preamble (self.messages[0])
            # and appends the last `max_messages` from the history.
            self.messages = [self.messages[0]] + self.messages[-(max_messages):]

    async def _moderate_text(self, text):
        """
        Calls the OpenAI Moderation API.
        Returns True if flagged, False otherwise.
        Fails safe (returns True) on error.
        """
        if not text:
            return False  # Do not flag empty strings
        try:
            response = self.client.moderations.create(
                model="omni-moderation-latest",
                input=text
            )
            result = response.results[0]
            return result.flagged
        except Exception as e:
            print(f"*** Moderation API call failed: {e}. Failing safe.")
            return True  # Fail-safe: assume text is flagged if API fails

    async def openai_query(self):
        if self.client is None:
            return

        # --- 1. Moderate User Input ---
        user_query_text = ""
        # Find the last user message to moderate it
        if self.messages and self.messages[-1]['role'] == 'user':
            user_query_content = self.messages[-1]['content']
            # Handle both string and list content (for images)
            if isinstance(user_query_content, list):
                # Find the text part in the list
                for part in user_query_content:
                    if part.get('type') == 'text':
                        user_query_text = part.get('text', '')
                        break
            elif isinstance(user_query_content, str):
                user_query_text = user_query_content

        if user_query_text and self.use_moderation:
            print('moderate input')
            user_flagged = await self._moderate_text(user_query_text)
            if user_flagged:
                print("*** User input flagged by moderation.")
                # Remove the flagged user message.
                self.messages.pop()
                # Also remove the system world_map prompt that preceded it.
                if self.messages and self.messages[-1]['role'] == 'system':
                    self.messages.pop()
                
                # Post a canned, safe response and stop.
                safe_answer = "I'm sorry, I can't talk about that topic."
                event = OpenAIEvent(safe_answer)
                self.robot.erouter.post(event)
                return

        # --- 2. Trim History ---
        # Call trim_history *after* user check, *before* API call.
        self._trim_history()

        # --- 3. Call Completion API ---
        try:
            response = self.client.chat.completions.create(
                model = self.model,
                messages = self.messages
            )
            answer = response.choices[0].message.content
        except Exception as e:
            print(f"*** OpenAI completion call failed: {e}")
            # Post a generic error and stop.
            safe_answer = "I'm sorry, I had trouble generating a response."
            event = OpenAIEvent(safe_answer)
            self.robot.erouter.post(event)
            return

        # --- 4. Moderate Assistant Output ---
        if self.use_moderation:
            print('moderate output')
            assistant_flagged =  await self._moderate_text(answer)
        else:
            assistant_flagged = False
        if assistant_flagged:
            print("*** Assistant output flagged by moderation.")
            # Do NOT append the flagged answer to history.
            # Post a canned, safe response and stop.
            safe_answer = "I'm sorry, I can't generate a response about that."
            event = OpenAIEvent(safe_answer)
            self.robot.erouter.post(event)
            return

        # --- 5. Process Good Response ---
        # If both checks pass, append the good answer to history.
        self.messages.append({'role': 'assistant', 'content': answer})
        
        # remove LaTeX brackets from response
        cleaned_answer = re.sub(r'\\[\[\]\(\)]', '', answer)
        event = OpenAIEvent(cleaned_answer)
        self.robot.erouter.post(event)

    # One-shot version doesn't use preamble or maintain message history

    def oneshot_query(self, query_text, image=None):
        self.robot.loop.call_soon_threadsafe(self.launch_openai_oneshot_query, query_text, image)


    def launch_openai_oneshot_query(self, query_text, image=None):
        self.robot.loop.create_task(self.openai_oneshot_query(query_text, image))

    async def openai_oneshot_query(self, query_text, image=None):
        if self.client is None:
            return
        content = [ {'type': 'text', 'text': query_text } ]
        if image is not None:
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 95]
            swapped_colors = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            result, encimg = cv2.imencode('.jpg', swapped_colors, encode_param)
            base64_image = base64.b64encode(encimg).decode('utf-8')
            content.append({'type': 'image_url',
                            'image_url': {'url': f'data:image/jpeg;base64,{base64_image}'}})
        messages = [ {'role': 'user',
                      'content': content } ]
        response = self.client.chat.completions.create(
            model = self.model,
            messages = messages
        )
        answer = response.choices[0].message.content
        cleaned_answer = re.sub(r'\\[\[\]\(\)]', '', answer)
        event = OpenAIEvent(cleaned_answer)
        self.robot.erouter.post(event)
