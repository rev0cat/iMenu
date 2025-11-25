"""
Mock LLM client for local development and testing.
"""
import time
import json
import random
from typing import Iterable, Dict, Any, Optional

import config
from llm.base import LLMClient


class MockLLMClient:
    """
    Mock LLM client that returns predefined responses for testing.
    """
    
    def __init__(self, delay: float = 0.1):
        """
        Initialize mock client.
        
        Args:
            delay: Delay between stream chunks in seconds.
        """
        self.delay = delay
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate a mock response based on prompt context."""
        # Simulate some processing time
        time.sleep(self.delay)
        
        # Return different responses based on prompt content
        prompt_lower = prompt.lower()
        
        if "dish plan" in prompt_lower or "菜品方案" in prompt_lower:
            return self._mock_dish_plan()
        elif "cooking steps" in prompt_lower or "烹饪步骤" in prompt_lower:
            return self._mock_cooking_steps()
        elif "expert opinion" in prompt_lower or "专家意见" in prompt_lower:
            return self._mock_expert_opinion(kwargs.get("expert_name", "专家"))
        elif "objection" in prompt_lower or "异议" in prompt_lower:
            return self._mock_objection()
        elif "chair decision" in prompt_lower or "主席裁决" in prompt_lower:
            return self._mock_chair_decision()
        elif "follow" in prompt_lower or "追问" in prompt_lower:
            return self._mock_followup_answer()
        else:
            return "这是一个模拟的LLM响应。在生产环境中，这将由真实的LLM生成。"
    
    def generate_stream(self, prompt: str, **kwargs) -> Iterable[str]:
        """Generate streaming mock response."""
        response = self.generate(prompt, **kwargs)
        
        # Split response into chunks for streaming simulation
        words = response.split()
        chunk_size = max(1, len(words) // 10)
        
        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i+chunk_size])
            if i > 0:
                chunk = " " + chunk
            time.sleep(self.delay)
            yield chunk
    
    def _mock_dish_plan(self) -> str:
        """Generate mock dish plan."""
        plans = [
            {
                "name": "蒜蓉西兰花炒鸡胸肉",
                "cuisine": "中式家常菜",
                "rationale": "这道菜结合了高蛋白的鸡胸肉和富含维生素的西兰花，符合健康饮食的要求。蒜蓉提味，简单易做。",
                "high_level_steps": [
                    "准备食材：切鸡胸肉、洗西兰花、切蒜末",
                    "腌制鸡胸肉",
                    "焯水西兰花",
                    "热锅炒鸡胸肉",
                    "加入西兰花和调味料翻炒",
                    "装盘出锅"
                ]
            },
            {
                "name": "番茄鸡蛋面",
                "cuisine": "中式面食",
                "rationale": "经典的家常面食，番茄富含番茄红素，鸡蛋提供优质蛋白，简单快手又营养均衡。",
                "high_level_steps": [
                    "准备食材：切番茄、打蛋液",
                    "炒鸡蛋盛出备用",
                    "炒番茄出汁",
                    "加水煮开",
                    "下面条煮熟",
                    "加入鸡蛋和调味料"
                ]
            }
        ]
        return json.dumps(random.choice(plans), ensure_ascii=False, indent=2)
    
    def _mock_cooking_steps(self) -> str:
        """Generate mock cooking steps."""
        steps = [
            {
                "index": 1,
                "title": "准备食材",
                "description": "将所有食材清洗干净，按需切配",
                "actions": ["清洗食材", "切配蔬菜", "肉类切片"],
                "tools_used": ["菜刀", "砧板"],
                "ingredients_used": ["主料", "配料"],
                "time_estimate_min": 10,
                "tips": "肉类逆纹理切，口感更嫩",
                "safety_notes": "注意刀具安全"
            },
            {
                "index": 2,
                "title": "热锅炒制",
                "description": "大火热锅，快速翻炒",
                "actions": ["热锅", "加油", "快速翻炒"],
                "tools_used": ["炒锅", "锅铲"],
                "ingredients_used": ["主料"],
                "time_estimate_min": 5,
                "tips": "火候要大，动作要快",
                "safety_notes": "小心油溅"
            }
        ]
        return json.dumps(steps, ensure_ascii=False, indent=2)
    
    def _mock_expert_opinion(self, expert_name: str) -> str:
        """Generate mock expert opinion."""
        opinions = {
            "大厨专家": "从烹饪技术角度来看，这个方案的火候控制很关键。建议在炒制过程中保持大火，快速翻炒以保持食材的脆嫩口感。",
            "营养专家": "这道菜的营养搭配比较均衡。建议可以适当减少油量，以控制总热量摄入。",
            "工具专家": "建议使用不粘锅以减少油量使用，同时确保锅具预热充分。",
            "新手教练": "这道菜难度适中，新手可以尝试。建议先将所有食材准备好再开始烹饪，避免手忙脚乱。",
            "安全专家": "烹饪时请注意油温，避免油温过高导致油烟。建议开启抽油烟机并保持通风。"
        }
        return opinions.get(expert_name, f"{expert_name}认为这个方案整体可行，建议继续优化细节。")
    
    def _mock_objection(self) -> str:
        """Generate mock objection."""
        return json.dumps({
            "has_objection": random.choice([True, False]),
            "reason": "火候建议可能对新手来说难以掌握",
            "severity": random.choice(["minor", "major"]),
            "suggestion": "建议增加具体的时间指导"
        }, ensure_ascii=False, indent=2)
    
    def _mock_chair_decision(self) -> str:
        """Generate mock chair decision."""
        return "经过综合评估各位专家的意见，主席决定采纳大部分建议。最终方案保持原有框架，同时增加了详细的时间指导和安全提示。"
    
    def _mock_followup_answer(self) -> str:
        """Generate mock follow-up answer."""
        return "根据您的追问，专家委员会进行了讨论。我们建议您可以根据个人口味调整调味料的用量。如果您喜欢更浓郁的味道，可以适当增加蒜末和酱油的用量。"


def get_llm_client() -> LLMClient:
    """
    Factory function to get the configured LLM client.
    """
    if config.LLM_PROVIDER == "mock":
        return MockLLMClient()
    # Add other providers here (OpenAI, etc.)
    else:
        return MockLLMClient()
