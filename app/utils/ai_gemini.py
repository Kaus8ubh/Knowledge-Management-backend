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
                    Consider the given collection of documents as a single document. 
                    A researcher needs a structured overview of this document. 
                    Generate a well-organized summary with clear sections of the following: \n\n
                    {combined_summary}
                    \n\n**Expected format:**
                    - Introduction: A brief about the content.
                    - Key Highlights: Use bullet points to list core ideas, facts, or methods.
                    - Conclusion: A short closing remark, if necessary.
                    Don't use decoratives in the summary.
                    Only include the main content of the topic; avoid promotional text.
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
