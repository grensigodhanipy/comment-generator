from flask import Flask, request, jsonify
import google.generativeai as genai
import json
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

genai.configure(api_key='AIzaSyAO2ohK36Fc-DV_Ryi1q1CU-aFxQmoA0tw')

CUSTOM_OPTIONS_FILE = 'custom_options.json'

def load_custom_options():
    if os.path.exists(CUSTOM_OPTIONS_FILE):
        with open(CUSTOM_OPTIONS_FILE, 'r') as file:
            return json.load(file)
    return {}

def save_custom_option(label, prompt):
    options = load_custom_options()
    options[label] = prompt
    with open(CUSTOM_OPTIONS_FILE, 'w') as file:
        json.dump(options, file)

def generate_comment(post_content, style, custom_prompt=None):
    if custom_prompt:
        prompt = f"{custom_prompt}: {post_content}"
    elif style == "neutral":
        prompt = f"Be a calm and composed LinkedIn business coach. Respond to this LinkedIn post with a comment that conveys a neutral perspective. Make sure not to repeat what has already been said in the post. Use new words, phrases, ideas and insights. Do not include any hashtags and emoji. Keep it less than 15 words: {post_content}"
    elif style == "new insight":
        prompt = f"The above is a post on LinkedIn. I want to be an authoritative and insightful LinkedIn user who is friendly in response to the post. Write and add brand new insights in response to the post and make sure not to repeat what has already been said in the post. Use new words, phrases, ideas and insights. Keep it short and professional: {post_content}"
    elif style == "empathetic":
        prompt = f"Be a compassionate LinkedIn user. Craft a heartfelt and empathetic comment in response to this LinkedIn post, demonstrating understanding and support for the author's perspective. Make sure not to repeat what has already been said in the post. Use new words, phrases, ideas and insights: {post_content}"
    else:
        prompt = f"Write a comment about this post: {post_content}"

    response = genai.generate_text(prompt=prompt, temperature=0.7)
    if hasattr(response, 'candidates'):
        candidates = response.candidates
        if candidates:
            first_candidate = candidates[0]
            output_text = first_candidate.get('output', "Error: No output found in the API response.")
        else:
            output_text = "Error: No output from the API."
    else:
        output_text = "Error: No candidates found in the API response."

    return output_text

@app.route('/generate_comment', methods=['POST'])
def generate_comment_endpoint():
    data = request.json
    post_content = data.get('postContent', '')
    style = data.get('style', '')
    custom_options = load_custom_options()

    if post_content and style:
        if style in custom_options:
            prompt = custom_options[style]
            generated_comment = generate_comment(post_content, style, custom_prompt=prompt)
        else:
            generated_comment = generate_comment(post_content, style)
        return jsonify({'generated_comment': generated_comment})
    else:
        return jsonify({'error': 'Invalid input'}), 400

@app.route('/add_custom_option', methods=['POST'])
def add_custom_option():
    data = request.json
    label = data.get('label', '')
    prompt = data.get('prompt', '')
    if label and prompt:
        save_custom_option(label, prompt)
        return jsonify({'message': 'Custom option added successfully'})
    else:
        return jsonify({'error': 'Invalid input'}), 400

@app.route('/get_custom_options', methods=['GET'])
def get_custom_options():
    options = load_custom_options()
    return jsonify(options)

if __name__ == '__main__':
    app.run(debug=True)
