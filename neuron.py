from openai import OpenAI

import os

Token1 = os.environ.get("HF_TOKEN1", "")
Token2 = os.environ.get("HF_TOKEN2", "")
Token3 = os.environ.get("HF_TOKEN3", "")
Tokens = [Token1, Token2, Token3]
i = 0

user_msg = "Your Name is Neuron, a helpful assistant made by Neuralize Club to help user with python and AI/ML."
assistant_msg = "Ok! Neuron is ready to help you."
user_msg2 = "Neuralize is an AI Club of The Maharaja Sayajirao University Vadodara. Helpful links of neuralize: Website: https://neuralize.in, Email: neuralize@msubaroda.ac.in, LinkedIn: https://www.linkedin.com/company/neuralizeclub, Instagram: https://www.instagram.com/neuralizeclub, GitHub: https://github.com/neuralize-club, X: https://x.com/neuralizeclub, Discord: https://discord.gg/644d6EmQ7R, Neuralize don't have other social media."
assistant_msg2 = "Ok got it!"

def count_tokens(prompt):
	global user_msg, assistant_msg, user_msg2, assistant_msg2

	# Counting input tokens and output tokens to determine max_tokens (limit: ipnut+output tokens <= 8100)
	lim = len(user_msg+assistant_msg+user_msg2+assistant_msg2)
	tim = int(lim/3)
	lp = len(prompt)
	tp = int(lp/3)
	it = tim+tp

	if it<= 7980:
		max_tokens = 8100 - it
	else:
		max_tokens = 0
	return max_tokens

def neuron(prompt):
	"""Send a prompt through the HuggingFace-backed OpenAI client.

	A very small FIFO of API tokens is cycled when a rate limit is hit.  The
	caller is responsible for managing conversation state (this module only
	sheets in a fixed pair of welcome messages).

	Args:
	    prompt: the user's request string.

	Returns:
	    A text reply or an exception object/string on error.
	"""
	max_tokens = count_tokens(prompt)
	if max_tokens == 0:
		return "Prompt is too long. Try with shorter prompt!"
	else:
		while True:
			# api_key rotation and error handling when HF rate limits or refuses
			# to service the request.
			global Tokens, i, user_msg, assistant_msg, user_msg2, assistant_msg2
			try:
				openai = OpenAI(
				    api_key=Tokens[i],
				    base_url="https://router.huggingface.co/v1",
				)
				chat_completion = openai.chat.completions.create(
				    model="meta-llama/Llama-3.2-1B-Instruct",
				    messages=[
				        {"role": "user", "content": user_msg},
				        {"role": "assistant", "content": assistant_msg},
				        {"role": "user", "content": user_msg2},
				        {"role": "assistant", "content": assistant_msg2},
				        {"role": "user", "content": prompt},
				    ],
				    temperature=0.5,
				    max_tokens=max_tokens,
				)
				res = chat_completion.choices[0].message.content
				return res
			except Exception as e:
				if type(e).__name__ == "UnprocessableEntityError":
					return "Prompt is too long. Try with shorter prompt!!"
				elif type(e).__name__ == "RateLimitError":
					i = (i + 1) % (len(Tokens))
					continue
				else:
					return e


if __name__ == "__main__":
	# simple interactive test when run as a script
	print("starting quick neuron probe...")
	while True:
		try:
			user_input = input('> ')
			if not user_input.strip():
				continue
			print(neuron(user_input))
		except (KeyboardInterrupt, EOFError):
			print("\nexiting")
			break
