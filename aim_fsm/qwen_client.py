import os
import re
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

# Matches a leading <think>...</think> block (Qwen3 thinking output) so it can
# be stripped before the answer is parsed/spoken. Suppressing it at the prompt
# level (/no_think) is the primary defense; this is a belt-and-suspenders cleanup.
THINK_BLOCK = re.compile(r'^\s*<think>.*?</think>\s*', re.DOTALL)


class QwenClient():
    """Drop-in replacement for OpenAIClient that talks to a local Ollama server
    running Qwen3-8B via Ollama's OpenAI-compatible API.

    Differences from OpenAIClient:
      - Points at http://localhost:11434/v1 instead of OpenAI's cloud endpoint.
      - No moderation API (Ollama doesn't expose one); use_moderation is ignored.
      - Qwen3 'thinking' is disabled so <think> blocks don't corrupt downstream
        hashtag-routing parsing.
      - Vision methods are kept (for interface compatibility with robot.py) but
        degrade honestly: Qwen3-8B cannot see images; Python CV handles vision
        elsewhere.
    """

    VISION_UNAVAILABLE_NOTE = (
        "Vision is unavailable on the local Qwen backend; "
        "no camera image was sent to the model."
    )

    DEFAULT_MODEL = 'qwen3:8b'
    DEFAULT_BASE_URL = 'http://localhost:11434/v1'

    def __init__(self, robot, model=DEFAULT_MODEL, use_moderation=False,
                 base_url=None, no_think=True):
        self.robot = robot
        self.model = model
        # use_moderation is accepted for signature compatibility but unused:
        # Ollama provides no moderation endpoint.
        self.use_moderation = False
        self.no_think = no_think
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL") or self.DEFAULT_BASE_URL
        # Uses the openai Python SDK as an HTTP client only; requests go to Ollama,
        # not to api.openai.com. There is no fallback to OpenAI cloud.
        api_key = os.getenv("OLLAMA_API_KEY") or "ollama"
        try:
            self.client = openai.OpenAI(base_url=self.base_url, api_key=api_key)
            print(f"*** QwenClient ready: model={self.model}  endpoint={self.base_url}")
        except Exception as e:
            print(f"*** Could not initialize Qwen/Ollama client: {e}")
            self.client = None
        self.set_preamble(default_preamble)

    def set_preamble(self, preamble):
        self.messages = [
            {'role': 'system', 'content': preamble}
        ]

    def _apply_no_think(self, text):
        """Append /no_think to the user turn to suppress Qwen3 reasoning output."""
        if self.no_think and isinstance(text, str):
            return text + " /no_think"
        return text

    def query(self, query_text):
        self.messages.append({'role': 'system', 'content': self.robot.world_map.get_prompt()})
        self.messages.append({'role': 'user', 'content': self._apply_no_think(query_text)})
        self.robot.loop.call_soon_threadsafe(self.launch_qwen_query)

    def note_for_later(self, text):
        self.messages.append({'role': 'system', 'content': text})

    def _note_vision_unavailable(self):
        self.messages.append(
            {'role': 'system', 'content': self.VISION_UNAVAILABLE_NOTE})

    # --- Vision methods: interface-compatible, honestly degraded. ---

    def camera_query(self, query_text):
        print("*** QwenClient.camera_query: vision not supported on Qwen backend.")
        self._note_vision_unavailable()
        self.messages.append(
            {'role': 'user',
             'content': self._apply_no_think(f"[Vision unavailable] {query_text}")})
        self.robot.loop.call_soon_threadsafe(self.launch_qwen_query)

    def send_camera_image(self, instruction=None):
        # Celeste FSM follows this with AskGPT(); do not launch a query here
        # (avoids a duplicate completion and a fake "here is the image" prompt).
        print("*** QwenClient.send_camera_image: vision not supported on Qwen backend.")
        self._note_vision_unavailable()

    def launch_qwen_query(self):
        self.robot.loop.create_task(self.qwen_query())

    def _trim_history(self, max_messages=200):
        """Keep the system preamble (index 0) and the last `max_messages`."""
        if len(self.messages) > (max_messages + 1):
            self.messages = [self.messages[0]] + self.messages[-(max_messages):]

    def _strip_think(self, text):
        if text is None:
            return text
        return THINK_BLOCK.sub('', text)

    async def qwen_query(self):
        if self.client is None:
            return

        self._trim_history()

        try:
            print(f"*** QwenClient query -> {self.base_url}  model={self.model}")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                # Belt-and-suspenders: some Ollama/Qwen builds honor this flag.
                extra_body={"chat_template_kwargs": {"enable_thinking": not self.no_think}},
            )
            answer = response.choices[0].message.content
        except Exception as e:
            print(f"*** Qwen completion call failed: {e}")
            safe_answer = "I'm sorry, I had trouble generating a response."
            event = OpenAIEvent(safe_answer)
            self.robot.erouter.post(event)
            return

        answer = self._strip_think(answer)

        # Append the (cleaned) answer to history.
        self.messages.append({'role': 'assistant', 'content': answer})

        # remove LaTeX brackets from response
        cleaned_answer = re.sub(r'\\[\[\]\(\)]', '', answer)
        event = OpenAIEvent(cleaned_answer)
        self.robot.erouter.post(event)

    # One-shot version doesn't use preamble or maintain message history

    def oneshot_query(self, query_text, image=None):
        self.robot.loop.call_soon_threadsafe(self.launch_qwen_oneshot_query, query_text, image)

    def launch_qwen_oneshot_query(self, query_text, image=None):
        self.robot.loop.create_task(self.qwen_oneshot_query(query_text, image))

    async def qwen_oneshot_query(self, query_text, image=None):
        if image is not None:
            print("*** QwenClient.oneshot_query: vision not supported on Qwen backend.")
            event = OpenAIEvent(
                "I'm sorry, I can't process images with the local language model."
            )
            self.robot.erouter.post(event)
            return
        if self.client is None:
            return
        messages = [{'role': 'user', 'content': self._apply_no_think(query_text)}]
        try:
            print(f"*** QwenClient oneshot -> {self.base_url}  model={self.model}")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                extra_body={"chat_template_kwargs": {"enable_thinking": not self.no_think}},
            )
            answer = response.choices[0].message.content
        except Exception as e:
            print(f"*** Qwen oneshot call failed: {e}")
            event = OpenAIEvent("I'm sorry, I had trouble generating a response.")
            self.robot.erouter.post(event)
            return
        answer = self._strip_think(answer)
        cleaned_answer = re.sub(r'\\[\[\]\(\)]', '', answer)
        event = OpenAIEvent(cleaned_answer)
        self.robot.erouter.post(event)