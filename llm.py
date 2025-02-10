class WebpageSummarizer:
    
    from openai import OpenAI
    def __init__(self, api_key):
        import os
        from openai import OpenAI    
        """
        Initialisiert die WebpageSummarizer-Klasse mit einem OpenAI API-Key.
        """
        self.client = OpenAI(api_key=api_key)

    def summarize(self, webpage_text):
        """
        Erstellt eine Zusammenfassung des Website-Texts mit maximal 100 Wörtern.
        """
        system_prompt = (
            "Du bist ein professioneller Texter, der prägnante Zusammenfassungen schreibt. "
            "Erstelle eine präzise, informative Zusammenfassung des folgenden Website-Inhalts in maximal 100 Wörtern. "
            "Die Zusammenfassung sollte die wichtigsten Punkte der Webseite enthalten."
        )
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": webpage_text},
        ]
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            max_tokens=150  # ca. 100 Wörter
        )
        
        return response.choices[0].message.content.strip()




