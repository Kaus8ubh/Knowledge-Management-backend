import json
import google.generativeai as genai
import re
from app.config import Config

class TextProcessingWithGemini:
    
    def __init__(self):
        # Load API key from Config
        self.api_key = Config.GEMINI_API_KEY 
        genai.configure(api_key=self.api_key)

    def extract_text_from_response(self, response):
        """
        Usage: Extracts text from a GenerateContentResponse object.
        Parameters: Generate Response object from the model.
        Returns: Extracted text from the response.
        """
        if response and response.candidates:
            candidate = response.candidates[0]
            if candidate.content and candidate.content.parts:
                part_texts = [part.text for part in candidate.content.parts if part.text]
                return "".join(part_texts)
        return ""  # Return an empty string if extraction fails

    def generate_tags(self, content, max_tags=5):
        """
        Usage: Generate tags from the provided content.
        Parameters:
            content (str): The content for which tags are to be generated.
            max_tags (int): The maximum number of tags to generate.
        Returns:
            list: A list of generated tags.
        """
        try:
            client = genai.GenerativeModel("gemini-2.0-flash")

            response = client.generate_content(f"""
                Generate tags for the following content:
                
                {content}
                
                ### Tagging Guidelines:
                1. Provide tags that accurately describe the content.
                2. Include only major topics and keywords.
                3. Avoid duplicates.
                4. Only give the top {max_tags} tags.
                5. Return the tags as a comma-separated list (e.g., AI, Machine Learning, Deep Learning).
            """)

            tags = self.extract_text_from_response(response)
            return [tag.strip() for tag in tags.split(",") if tag.strip()]
        except Exception as exception:
            print(f"Error generating tags: {exception}")
            return None
    
    
    def summarize_text(self, chunks):
        """
        Usage: Summarize text chunks into a structured format.
        Parameters:
            chunks (list): A list of text chunks to be summarized.
        Returns:
            str: The final summary of the text chunks.
        """
        try:
            client = genai.GenerativeModel("gemini-2.0-flash")

            summary_texts = []
            for chunk in chunks:
                response = client.generate_content(f"Summarize the following content thoroughly in a structured manner:\n\n{chunk}")
                summary_text = self.extract_text_from_response(response)
                summary_texts.append(summary_text)

                combined_summary = "\n\n".join(summary_texts)

                # Generate a refined summary in a structured format
                response = client.generate_content(f"""
                            You are provided with a collection of documents that together form a single comprehensive document.
                            A researcher needs a summary that is informative, clear, and structured in a visually engaging format using emojis and headings. Your task is to generate a rich, self-contained summary that does not require the reader to refer back to the original documents.

                            **Required Output Format:**

                            **Summary**  
                            Write a concise 1–2 sentence overview that clearly explains what the document is about, its main focus, and what the reader will learn.

                            **Highlights**  
                            List the most important features, concepts, or components using bullet points with relevant emojis.  
                            Each bullet should be 1-2 sentence long and written in a simple, clear style.

                            Example format:  
                            🌐 Domain and Hosting: Acquire a domain name and hosting for your website.

                            **Key Insights**  
                            Provide an expanded explanation of the core ideas or methods introduced in the content.  
                            Each bullet point should start with an emoji and bolded heading, followed by 2–4 explanatory sentences.  
                            If any processes, frameworks, or systems are described, explain them clearly.  
                            Use examples when they help make the concept easier to understand.

                            Example format:  
                            🌍 **Understanding Domain and Hosting**: A domain is your website’s address, while hosting is the service that stores your site files. Both are essential for getting your site online. Choosing the right provider ensures good performance and security.

                            **Guidelines:**  
                            - Use emojis to help structure and clarify the content visually.  
                            - Maintain a professional but friendly and educational tone.  
                            - Avoid promotional language.  
                            - Do not include extra preamble like “Here’s the summary…” — just present the sections directly.  
                            - Ensure the summary is self-contained and stands alone.

                            Summarize the following document in this format:

                            {combined_summary}

                        """)


                final_summary = self.extract_text_from_response(response)

                return final_summary

        except Exception as exception:
            print(f"Error summarizing text: {exception}")
            return None


    def get_title(self, summary):
        """
        Usage: Generate a title based on the provided summary.
        parameters:
            summary (str): The summary of the content.
        Returns:
            str: title.
        """
        try:
            client = genai.GenerativeModel("gemini-2.0-flash")

            response = client.generate_content(f"""
                Generate a concise and engaging title based on the following summary:
                Give only single title in return
                
                {summary}
                
                ### Title Guidelines:
                1. Short & Catchy: Keep the title concise and attention-grabbing.
                2. Reflect the Summary: Ensure the title accurately represents the main idea.
                3. Avoid Clickbait: The title should be informative.
                4. Max 6 Words: Keep the title brief and impactful.
            """)

            title = self.extract_text_from_response(response)
            
            # Remove "**Title:**" or "*Title:*" if present
            return re.sub(r"^\**Title:\**\s*", "", title).strip("*")
        except Exception as exception:
            print(f"Error generating title: {exception}")
            return None

    def generate_category(self, content):
        """
        Usage: Generate a single category based on the provided content, ensuring
            the category is one of the predefined categories or "Uncategorized".
        Parameters:
            content (str): The content for which category is to be generated.
        Returns:
            str: A category type (e.g., Tech, Social, Science, etc.) or "Uncategorized".
        """
        try:
            # List of predefined categories
            predefined_categories = [
                "tech", "science", "health", "business", "politics", 
                "entertainment", "sports", "education", "travel", "food", 
                "lifestyle", "fashion", "music", "movies", "gaming", 
                "news", "environment", "social media", "finance", "art"
            ]

            client = genai.GenerativeModel("gemini-2.0-flash")

            # Request category generation
            response = client.generate_content(f"""
                    Categorize the following content into one of these predefined categories:
                    technology, science, health, business, politics, entertainment, sports,
                    education, travel, food, lifestyle, fashion, music, movies, gaming,
                    news, environment, social media, finance, art.
                    {content}
                    ### Category Guidelines:
                    1. Choose only one category from the predefined list.
                    2. Provide the most relevant category that best describes the content.
                    3. Return the category as a single word (e.g., tech, news, science).
                    """)

            category = self.extract_text_from_response(response).strip()

            # If the generated category is not in predefined categories, set it as "Misc"
            if category not in predefined_categories:
                category = "Misc"

            return category
        except Exception as exception:
            print(f"Error generating category: {exception}")
            return None
        
    def generate_qna(self, content):
        """
        Usage: Generate a Q&A format from the provided content.
        Parameters:
            content (str): The content for which Q&A is to be generated.
        Returns:
            str: A Q&A format based on the content.
        """
        try:
            client = genai.GenerativeModel("gemini-2.0-flash")

            response = client.generate_content(f"""
                        You are an expert content summarizer and educator. From the following content, extract valuable knowledge and generate **detailed and explanatory Q&A pairs** suitable for someone trying to learn or revise the topic deeply.

                        ### Instructions:
                        1. Each question should be insightful and encourage understanding.
                        2. Each answer should be descriptive, ideally 2–5 sentences, and include examples or explanations if applicable.
                        3. Avoid list-only or single-line answers unless absolutely necessary.
                        4. Ensure clarity, context, and educational value in each Q&A.
                        5. Provide at least 5 meaningful Q&A pairs.

                        Content:
                        \"\"\"
                        {content}
                        \"\"\"
                        Format the output as a list of questions and answers.

                        No headers, no markdown, just plain text format.
                    """)

            raw_qna_text = self.extract_text_from_response(response)

            qna_list = self.parse_qna_to_list(raw_qna_text)
            return qna_list
        except Exception as exception:
            print(f"Error generating Q&A: {exception}")
            return None

    def answer_custom_question(self, content, question):
        """
        Answers a custom question based on the provided content.
        Returns a clear, direct answer for questions related to the content,
        or a respectful message if the question is completely unrelated.
        """
        try:
            client = genai.GenerativeModel("gemini-2.0-flash")

            prompt = f"""
                You are a helpful and accurate assistant. A user will ask a question based on the provided content.

                Rules:
                - Answer questions that are directly related OR tangentially related to the content
                - If the question is about a topic mentioned in the content, even briefly, provide a helpful answer
                - Feel free to make reasonable inferences based on the content
                - Use a conversational tone and light emojis 😊
                - Do not say "Based on the content..."—just answer as if you're chatting
                - If a question is gibberish or unclear, politely ask the user to rephrase 🤔
                - IMPORTANT: ONLY refuse to answer if the question is COMPLETELY unrelated to anything in the content
                - If refusing, briefly summarize what topics the content actually covers

                Examples of when to answer:
                - Question asks about something explicitly mentioned in content
                - Question asks for an opinion/explanation about a topic mentioned in content
                - Question asks about implications or related aspects of topics in content
                - Question asks for more details about something briefly mentioned

                Examples of when NOT to answer:
                - Question asks about a completely different subject with no connection to content
                - Question asks for information about topics with zero mention in the content

                ---
                Content:
                \"\"\"{content}\"\"\"

                Question:
                \"\"\"{question}\"\"\"

                Answer:
                """

            response = client.generate_content(prompt)
            answer = self.extract_text_from_response(response)
            return answer

        except Exception as exception:
            print(f"Error answering custom question: {exception}")
            return "There was an error processing your request. Please try again."

    def parse_qna_to_list(self, text):
        """
            Converts raw Q&A text into a structured list of Q&A dictionaries.        
        """
        pattern = re.compile(r"Q:\s*(.*?)\nA:\s*(.*?)(?=\nQ:|\Z)", re.DOTALL)
        matches = pattern.findall(text)

        qna_list = [{"question": q.strip(), "answer": a.strip()} for q, a in matches]
        return qna_list

    def generate_knowledge_map(self, content):
        """
        Usage: Generate a knowledge map from the provided content.
        Parameters:
            content (str): The content for which the knowledge map is to be generated.
        Returns:
            str: A knowledge map based on the content.
        """
        try:
            client = genai.GenerativeModel("gemini-2.0-flash")

            response = client.generate_content(f"""
                            I have the following summary of a topic:
                            {content}
                            Based on this summary, generate a detailed, beginner-friendly Knowledge Map in JSON format, structured like a learning guide.
                            Output JSON with this format:
                                {{   
                                    "knowledgeMap": [
                                        {{
                                        "section": "Prerequisite Topics",
                                        "icon": "📘",
                                        "items": [
                                            {{
                                            "topic": "Linear Algebra",
                                            "description": "Understand vectors and matrices, essential for neural network computations.",
                                            "difficulty": "🟡 Intermediate"
                                            }},
                                            ...
                                        ]
                                        }},
                                        ...
                                    ]
                                    }}
                            The sections should be: 📘 Prerequisite Topics, 🔍 Core Concepts, 🔗 Related Concepts, 🧰 Supplementary Topics, 🌐 Adjacent Areas

                            Each item should include:
                                topic (name of the concept)
                                description (brief explanation in beginner-friendly language)
                                difficulty (use one of: 🟢 Beginner, 🟡 Intermediate, 🔴 Advanced)
                    """)

            raw_knowledge_map = self.extract_text_from_response(response)
            knowledge_map = self.extract_knowledge_map(raw_knowledge_map)
            # Unwrap the "knowledgeMap" key safely
            if isinstance(knowledge_map, dict) and "knowledgeMap" in knowledge_map:
                return knowledge_map["knowledgeMap"]
            else:
                print("Unexpected knowledge_map format:", knowledge_map)
                return []
        except Exception as exception:
            print(f"Error generating knowledge map: {exception}")
            return None
        
    def extract_knowledge_map(self, raw_response: str):
        """
        Extracts clean JSON from a model response wrapped in a code block.
        """
        try:
            cleaned = re.sub(r'^```json\s*|\s*```$', '', raw_response.strip())
            # Convert to dictionary
            return json.loads(cleaned)
        
        except Exception as exception:
            return {"error": f"Failed to parse knowledge map: {str(exception)}"}