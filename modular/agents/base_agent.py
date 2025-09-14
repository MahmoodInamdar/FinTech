# Base Agent Class
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import pandas as pd
from openai import OpenAI

class BaseAgent(ABC):
    """Base class for all agents in the system"""

    def __init__(self, name: str, model_name: str = "gpt-3.5-turbo"):
        self.name = name
        self.model_name = model_name
        self.client = None

    def initialize_model(self, api_key: str):
        """Initialize the OpenAI client"""
        self.client = OpenAI(api_key=api_key)

    @abstractmethod
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input and return results"""
        pass

    def generate_response(self, prompt: str, max_tokens: int = 1000) -> str:
        """Generate response using OpenAI model"""
        if not self.client:
            return "Error: OpenAI client not initialized"

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.1  # Lower temperature for more consistent results
            )
            content = response.choices[0].message.content
            if not content:
                return "Error: Empty response from OpenAI"
            return content.strip()
        except Exception as e:
            error_msg = f"OpenAI API Error: {str(e)}"
            print(f"⚠️ {self.name}: {error_msg}")  # Debug logging
            return f"LLM_ERROR: {error_msg}"

    def analyze_dataframe(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze DataFrame and return basic statistics"""
        return {
            'shape': df.shape,
            'columns': list(df.columns),
            'dtypes': df.dtypes.to_dict(),
            'missing_values': df.isnull().sum().to_dict(),
            'summary': df.describe().to_dict() if len(df.select_dtypes(include=['number']).columns) > 0 else {},
            'sample_data': df.head().to_dict()
        }
