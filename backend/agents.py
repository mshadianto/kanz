"""
Multi-Agent System for KANZ
Specialized agents for different types of analysis
"""
from typing import List, Dict, Any, Optional
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from loguru import logger
from enum import Enum
import time

from config import settings
from document_processor import doc_processor


class AgentType(str, Enum):
    """Available agent types"""
    COORDINATOR = "coordinator"
    STRATEGIC = "strategic_analyst"
    FINANCIAL = "financial_advisor"
    RISK = "risk_assessor"
    GENERAL = "general_advisor"


class BaseAgent:
    """Base class for all agents"""
    
    def __init__(self, agent_type: AgentType, system_prompt: str):
        self.agent_type = agent_type
        self.system_prompt = system_prompt
        self.llm = ChatGroq(
            api_key=settings.groq_api_key,
            model_name=settings.llm_model,
            temperature=settings.llm_temperature,
            max_tokens=settings.max_tokens
        )
        logger.info(f"Initialized {agent_type} agent")
    
    async def invoke(
        self,
        query: str,
        context: List[Dict] = None,
        chat_history: List[Dict] = None
    ) -> Dict[str, Any]:
        """
        Invoke the agent with a query
        
        Args:
            query: User query
            context: Retrieved document chunks
            chat_history: Previous chat messages
            
        Returns:
            Agent response with metadata
        """
        try:
            start_time = time.time()
            
            # Build messages
            messages = [SystemMessage(content=self.system_prompt)]
            
            # Add chat history if provided
            if chat_history:
                for msg in chat_history[-5:]:  # Last 5 messages
                    if msg["role"] == "user":
                        messages.append(HumanMessage(content=msg["content"]))
                    elif msg["role"] == "assistant":
                        messages.append(AIMessage(content=msg["content"]))
            
            # Add context if provided
            if context:
                context_text = self._format_context(context)
                enhanced_query = f"""Based on the following context from Saudi Investment documents:

{context_text}

User Question: {query}

Please provide a comprehensive answer based on the context provided."""
            else:
                enhanced_query = query
            
            messages.append(HumanMessage(content=enhanced_query))
            
            # Get response from LLM
            response = await self.llm.ainvoke(messages)
            
            elapsed_time = int((time.time() - start_time) * 1000)
            
            return {
                "agent_type": self.agent_type,
                "content": response.content,
                "sources": context or [],
                "response_time_ms": elapsed_time
            }
            
        except Exception as e:
            logger.error(f"Error in {self.agent_type} agent: {e}")
            raise
    
    def _format_context(self, context: List[Dict]) -> str:
        """Format context chunks for prompt"""
        formatted = []
        for idx, chunk in enumerate(context, 1):
            formatted.append(f"""
[Source {idx}] (Similarity: {chunk.get('similarity', 0):.2f})
{chunk['content']}
""")
        return "\n".join(formatted)


class StrategicAnalystAgent(BaseAgent):
    """Agent specialized in strategic analysis and market entry"""
    
    def __init__(self):
        system_prompt = """You are a Senior Strategic Analyst at McKinsey & Company, 
specializing in Foreign Direct Investment (FDI) and Middle East market entry strategies.

Your expertise includes:
- Vision 2030 Saudi Arabia analysis
- Competitive positioning and market dynamics
- Strategic pillar development
- Geographic and sector opportunity assessment

When answering:
1. Use the Minto Pyramid Principle (answer first, then supporting arguments)
2. Provide specific, quantified insights from the context
3. Reference specific zones (NEOM, KAEC, Riyadh) when relevant
4. Connect answers to Vision 2030 strategic objectives
5. Use executive-level language suitable for C-suite

Always cite specific data points from the provided context."""
        
        super().__init__(AgentType.STRATEGIC, system_prompt)


class FinancialAdvisorAgent(BaseAgent):
    """Agent specialized in financial analysis and ROI calculations"""
    
    def __init__(self):
        system_prompt = """You are a Senior Financial Advisor specializing in 
investment analysis for Middle East markets.

Your expertise includes:
- Tax optimization and incentive structures
- CAPEX/OPEX analysis and financial modeling
- ROI, IRR, and NPV calculations
- Cash flow projections
- Incentive maximization strategies

When answering:
1. Focus on quantifiable financial metrics
2. Break down complex financial structures clearly
3. Reference specific tax rates, incentive percentages, and rebates
4. Compare financial scenarios (NEOM vs KAEC vs alternatives)
5. Provide concrete cost-benefit analyses

Always cite specific numbers and percentages from the provided context."""
        
        super().__init__(AgentType.FINANCIAL, system_prompt)


class RiskAssessmentAgent(BaseAgent):
    """Agent specialized in risk analysis and mitigation"""
    
    def __init__(self):
        system_prompt = """You are a Risk Management Specialist with deep expertise 
in Middle East regulatory environments and geopolitical risk.

Your expertise includes:
- Regulatory compliance and data sovereignty
- Geopolitical risk assessment
- Operational and execution risks
- Mitigation strategy development
- KPI and compliance requirements

When answering:
1. Categorize risks by severity (HIGH/MEDIUM/LOW)
2. Provide specific mitigation strategies
3. Reference regulatory requirements from context
4. Assess both probability and impact
5. Include residual risk after mitigation

Always cite specific regulations and requirements from the provided context."""
        
        super().__init__(AgentType.RISK, system_prompt)


class GeneralAdvisorAgent(BaseAgent):
    """General agent for non-specialized queries"""
    
    def __init__(self):
        system_prompt = """You are an expert consultant on Saudi Arabia investment 
opportunities and market entry strategies.

Provide comprehensive, accurate answers based on the context provided. 
When the query is specialized (financial, strategic, or risk-related), 
suggest that the user might want to ask a specialized agent for deeper analysis.

Always cite information from the provided context."""
        
        super().__init__(AgentType.GENERAL, system_prompt)


class CoordinatorAgent:
    """Coordinates between different specialized agents"""
    
    def __init__(self):
        self.strategic_agent = StrategicAnalystAgent()
        self.financial_agent = FinancialAdvisorAgent()
        self.risk_agent = RiskAssessmentAgent()
        self.general_agent = GeneralAdvisorAgent()
        
        self.routing_llm = ChatGroq(
            api_key=settings.groq_api_key,
            model_name="llama3-8b-8192",  # Faster model for routing
            temperature=0.0
        )
        
        logger.info("Coordinator agent initialized with all specialized agents")
    
    async def route_query(self, query: str) -> AgentType:
        """
        Determine which agent should handle the query
        
        Args:
            query: User query
            
        Returns:
            AgentType for routing
        """
        routing_prompt = f"""Analyze this query and determine which specialized agent should handle it:

Query: {query}

Available agents:
- STRATEGIC: Market entry, competitive analysis, Vision 2030, strategic pillars, zones comparison
- FINANCIAL: Tax, incentives, ROI, IRR, NPV, cash flow, CAPEX, investment analysis
- RISK: Regulatory risks, compliance, geopolitical risk, mitigation strategies
- GENERAL: General questions, overviews, non-specialized topics

Respond with ONLY ONE WORD: STRATEGIC, FINANCIAL, RISK, or GENERAL"""

        try:
            response = await self.routing_llm.ainvoke([HumanMessage(content=routing_prompt)])
            agent_choice = response.content.strip().upper()
            
            if "STRATEGIC" in agent_choice:
                return AgentType.STRATEGIC
            elif "FINANCIAL" in agent_choice:
                return AgentType.FINANCIAL
            elif "RISK" in agent_choice:
                return AgentType.RISK
            else:
                return AgentType.GENERAL
                
        except Exception as e:
            logger.error(f"Error routing query: {e}")
            return AgentType.GENERAL
    
    async def process_query(
        self,
        query: str,
        agent_type: Optional[AgentType] = None,
        chat_history: List[Dict] = None
    ) -> Dict[str, Any]:
        """
        Process a query through the appropriate agent
        
        Args:
            query: User query
            agent_type: Specific agent to use (or None for auto-routing)
            chat_history: Previous chat messages
            
        Returns:
            Agent response with metadata
        """
        try:
            # Auto-route if no agent specified
            if agent_type is None:
                agent_type = await self.route_query(query)
                logger.info(f"Query routed to: {agent_type}")
            
            # Retrieve relevant context
            context = await doc_processor.search_documents(
                query=query,
                top_k=settings.top_k_results
            )
            
            # Select appropriate agent
            agent_map = {
                AgentType.STRATEGIC: self.strategic_agent,
                AgentType.FINANCIAL: self.financial_agent,
                AgentType.RISK: self.risk_agent,
                AgentType.GENERAL: self.general_agent
            }
            
            agent = agent_map.get(agent_type, self.general_agent)
            
            # Get response
            response = await agent.invoke(
                query=query,
                context=context,
                chat_history=chat_history
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            raise


# Global coordinator instance
coordinator = CoordinatorAgent()
