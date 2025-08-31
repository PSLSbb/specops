#!/usr/bin/env python3
"""Test if the TaskGenerator has the format_tasks_markdown method."""

import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

def test_method_exists():
    """Test if the method exists."""
    try:
        from generators.task_generator import TaskGenerator, Task
        
        # Create instance
        generator = TaskGenerator()
        
        # Check if method exists
        if hasattr(generator, 'format_tasks_markdown'):
            print("✅ format_tasks_markdown method exists")
            
            # Test with empty tasks
            result = generator.format_tasks_markdown([])
            print(f"✅ Method works with empty list: {len(result)} characters")
            
            # Test with sample task
            sample_task = Task(
                title="Test Task",
                description="This is a test task",
                number=1,
                acceptance_criteria=["Complete the test"],
                prerequisites=["Have Python installed"]
            )
            
            result = generator.format_tasks_markdown([sample_task])
            print(f"✅ Method works with sample task: {len(result)} characters")
            print("\nSample output:")
            print(result[:200] + "..." if len(result) > 200 else result)
            
            return True
        else:
            print("❌ format_tasks_markdown method does NOT exist")
            print("Available methods:")
            for attr in dir(generator):
                if not attr.startswith('_'):
                    print(f"  - {attr}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing method: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_method_exists()
    sys.exit(0 if success else 1)