from langchain_core.language_models.llms import LLM
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from pydantic import Field
from typing import Any, List, Optional, Dict
import requests
import json
import re

class MOELLM(LLM):
    """MOE (Mixture of Experts) LLM for LangChain"""
    
    base_url: str = Field(default="http://localhost:5000", description="MOE API base URL")
    expert: str = Field(default="report", description="Expert type: 'report' or 'verify' or 'post_verify'")
    max_tokens: int = Field(default=512, description="Maximum tokens to generate")
    temperature: float = Field(default=0.7, description="Sampling temperature")
    
    @property
    def _llm_type(self) -> str:
        return "moe_llm"
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Call the MOE API"""
        url = f"{self.base_url}/generate/"
        payload = {
            "expert": self.expert,
            "prompt": prompt,
            "max_tokens": self.max_tokens
        }
        
        try:
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            result = response.json()
            
            # 提取文本内容，兼容不同的响应格式
            if isinstance(result, dict):
                if 'content' in result:
                    # 如果响应包含content字段，提取其中的文本
                    content = result['content']
                    if isinstance(content, str):
                        # 如果content是字符串，直接返回
                        return content
                    elif isinstance(content, dict) and 'assistant' in content:
                        # 如果content是字典且包含assistant字段
                        return content['assistant']
                    else:
                        # 其他情况，返回整个content的字符串表示
                        return str(content)
                elif 'text' in result:
                    return result['text']
                elif 'response' in result:
                    return result['response']
                else:
                    # 如果没有找到预期的字段，返回整个响应的字符串表示
                    return str(result)
            else:
                # 如果响应不是字典，直接转换为字符串
                return str(result)
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"MOE API调用失败: {e}")
    
    def invoke(self, prompt: str, **kwargs: Any) -> str:
        """Invoke method for LangChain compatibility"""
        return self._call(prompt, **kwargs)
    
    @property
    def _identifying_params(self) -> Dict[str, Any]:
        """Get the identifying parameters"""
        return {
            "base_url": self.base_url,
            "expert": self.expert,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature
        }

class MOEChain:
    """MOE Chain for easy expert switching"""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.experts = {}
        self._init_experts()
    
    def _init_experts(self):
        """Initialize expert LLMs"""
        self.experts["report"] = MOELLM(
            base_url=self.base_url,
            expert="report",
            max_tokens=512
        )
        self.experts["verify"] = MOELLM(
            base_url=self.base_url,
            expert="verify", 
            max_tokens=512
        )
    
    def get_expert(self, expert_type: str) -> MOELLM:
        """Get a specific expert"""
        if expert_type not in self.experts:
            raise ValueError(f"未知专家类型: {expert_type}. 可用类型: {list(self.experts.keys())}")
        return self.experts[expert_type]
    
    def generate_with_expert(self, expert_type: str, prompt: str) -> str:
        """Generate text with a specific expert"""
        expert = self.get_expert(expert_type)
        return expert._call(prompt)
    


def create_moe_chain(base_url: str = "http://localhost:5000") -> MOEChain:
    """Create a MOE chain instance"""
    return MOEChain(base_url=base_url) 



