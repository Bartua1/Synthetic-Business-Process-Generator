import requests
import json
from typing import List, Dict, Union, Optional

class LMStudioConnector:
    def __init__(self, ip: str = 'localhost', port: int = 1234):
        """Initialize the LM Studio connector.

        Args:
            ip (str): IP address of the LM Studio server. Defaults to 'localhost'.
            port (int): Port number of the LM Studio server. Defaults to 1234.
        """
        self.base_url = f"http://{ip}:{port}/v1/chat/completions"
        self.headers = {"Content-Type": "application/json"}

    def get_answer(
        self,
        message: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = -1,
        stream: bool = False
    ) -> Dict:
        """Send a message to LM Studio and get the response.

        Args:
            message (str): The user message to send
            system_prompt (str, optional): System prompt to set context. Defaults to None.
            temperature (float): Controls randomness in the response. Defaults to 0.7.
            max_tokens (int): Maximum tokens in response. -1 for unlimited. Defaults to -1.
            stream (bool): Whether to stream the response. Defaults to False.

        Returns:
            Dict: The JSON response from LM Studio

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        messages: List[Dict[str, str]] = []

        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })

        messages.append({
            "role": "user",
            "content": message
        })

        data = {
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream
        }

        response = requests.post(
            self.base_url,
            headers=self.headers,
            data=json.dumps(data)
        )

        if response.status_code == 200:
            # Return only the content of the last message
            return response.json()["choices"][0]["message"]["content"]
        else:
            raise requests.exceptions.RequestException(
                f"Request failed with status {response.status_code}: {response.text}"
            )