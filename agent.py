"""
AI Test Automation Agent
Coordinates parsing, execution, and reporting of browser automation tasks
"""

from parser import parse_input
from executor import run_test
from report import TestReport
import time
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AutomationAgent:
    """
    Manages the complete automation workflow:
    1. Parse user input into steps
    2. Execute automation
    3. Generate report
    """
    
    def __init__(self):
        self.last_report = None
        self.last_steps = None
        self.execution_history = []
    
    def execute_automation(self, instruction):
        """
        Main entry point for automation execution
        
        Args:
            instruction (str): Natural language instruction
            
        Returns:
            dict: Execution result with report and code
        """
        try:
            logger.info(f"[Agent] Processing instruction: {instruction[:100]}...")
            
            # Step 1: Parse instruction into automation steps
            steps = self._parse_instruction(instruction)
            if not steps:
                logger.error("[Agent] Parsing failed")
                return {
                    "error": "Failed to parse instruction",
                    "instruction": instruction,
                    "parsed": [],
                    "report": {},
                    "code": ""
                }
            
            logger.info(f"[Agent] Parsed {len(steps)} steps")
            self.last_steps = steps
            
            # Step 2: Execute automation
            report, code = self._run_automation(steps)
            
            # Step 3: Store history
            self._store_execution(instruction, steps, report)
            
            logger.info(f"[Agent] Execution complete: {report['status']}")
            
            return {
                "instruction": instruction,
                "parsed": steps,
                "report": report,
                "code": code
            }
            
        except Exception as e:
            logger.error(f"[Agent] Error: {str(e)}")
            return {
                "error": str(e),
                "instruction": instruction,
                "parsed": [],
                "report": {},
                "code": ""
            }
    
    def _parse_instruction(self, instruction):
        """Parse natural language instruction into steps"""
        try:
            steps = parse_input(instruction)
            return steps
        except Exception as e:
            logger.error(f"[Agent] Parsing error: {e}")
            return None
    
    def _run_automation(self, steps):
        """Execute automation steps"""
        try:
            report, code = run_test(steps)
            self.last_report = report
            return report, code
        except Exception as e:
            logger.error(f"[Agent] Execution error: {e}")
            raise
    
    def _store_execution(self, instruction, steps, report):
        """Store execution in history"""
        execution = {
            "timestamp": time.time(),
            "instruction": instruction,
            "steps_count": len(steps),
            "status": report.get("status", "UNKNOWN"),
            "execution_time": report.get("execution_time", 0),
            "total_steps": report.get("total_steps", 0)
        }
        self.execution_history.append(execution)
    
    def get_last_report(self):
        """Get the last execution report"""
        return self.last_report
    
    def get_execution_history(self):
        """Get all execution history"""
        return self.execution_history
    
    def get_execution_summary(self):
        """Get summary of all executions"""
        if not self.execution_history:
            return {
                "total_executions": 0,
                "successful": 0,
                "failed": 0,
                "average_time": 0
            }
        
        total = len(self.execution_history)
        successful = sum(1 for e in self.execution_history if e["status"] == "PASS")
        failed = total - successful
        avg_time = sum(e["execution_time"] for e in self.execution_history) / total if total > 0 else 0
        
        return {
            "total_executions": total,
            "successful": successful,
            "failed": failed,
            "average_time": round(avg_time, 2),
            "success_rate": f"{(successful/total*100):.1f}%" if total > 0 else "0%"
        }


# Global agent instance
_agent = None


def get_agent():
    """Get or create the global agent instance"""
    global _agent
    if _agent is None:
        _agent = AutomationAgent()
    return _agent


def execute(instruction):
    """Execute automation through the agent"""
    agent = get_agent()
    return agent.execute_automation(instruction)


def get_summary():
    """Get execution summary"""
    agent = get_agent()
    return agent.get_execution_summary()
