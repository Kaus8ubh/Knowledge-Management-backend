import google.generativeai as genai
import re
from config import Config

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
                "Tech", "Science", "Health", "Business", "Politics", 
                "Entertainment", "Sports", "Education", "Travel", "Food", 
                "Lifestyle", "Fashion", "Music", "Movies", "Gaming", 
                "News", "Environment", "Social Media", "Finance", "Art"
            ]

            client = genai.GenerativeModel("gemini-2.0-flash")

            # Request category generation
            response = client.generate_content(f"""
                    Categorize the following content into one of these predefined categories:
                    Technology, Science, Health, Business, Politics, Entertainment, Sports,
                    Education, Travel, Food, Lifestyle, Fashion, Music, Movies, Gaming,
                    News, Environment, Social Media, Finance, Art.
                    {content}
                    ### Category Guidelines:
                    1. Choose only one category from the predefined list.
                    2. Provide the most relevant category that best describes the content.
                    3. Return the category as a single word (e.g., Tech, News, Science).
                    """)

            category = self.extract_text_from_response(response).strip()

            # If the generated category is not in predefined categories, set it as "Misc"
            if category not in predefined_categories:
                category = "Misc"

            return category
        except Exception as exception:
            print(f"Error generating category: {exception}")
            return None
