"""Unit tests for TaskGenerator component."""

import pytest
from unittest.mock import Mock, patch
from pathlib import Path

from src.generators.task_generator import TaskGenerator, TaskDocument, Task
from src.models import TaskSuggestion, FeatureAnalysis


class TestTask:
    """Test cases for Task class."""
    
    def test_task_creation(self):
        """Test basic task creation."""
        task = Task(
            title="Test Task",
            description="A test task",
            acceptance_criteria=["Criterion 1", "Criterion 2"],
            prerequisites=["Prereq 1"],
            estimated_time=30,
            difficulty="medium"
        )
        
        assert task.title == "Test Task"
        assert task.description == "A test task"
        assert len(task.acceptance_criteria) == 2
        assert len(task.prerequisites) == 1
        assert task.estimated_time == 30
        assert task.difficulty == "medium"
        assert not task.completed
        assert task.number is None
        assert task.parent_number is None
    
    def test_task_full_number(self):
        """Test task number formatting."""
        # Main task
        main_task = Task(title="Main Task", number=1)
        assert main_task.get_full_number() == "1"
        
        # Subtask
        subtask = Task(title="Subtask", number=2, parent_number=1)
        assert subtask.get_full_number() == "1.2"
        
        # Task without number
        no_number_task = Task(title="No Number")
        assert no_number_task.get_full_number() == ""
    
    def test_add_subtask(self):
        """Test adding subtasks to a task."""
        main_task = Task(title="Main Task", number=1)
        subtask1 = Task(title="Subtask 1")
        subtask2 = Task(title="Subtask 2")
        
        main_task.add_subtask(subtask1)
        main_task.add_subtask(subtask2)
        
        assert len(main_task.subtasks) == 2
        assert subtask1.parent_number == 1
        assert subtask1.number == 1
        assert subtask2.parent_number == 1
        assert subtask2.number == 2
        assert subtask1.get_full_number() == "1.1"
        assert subtask2.get_full_number() == "1.2"
    
    def test_prerequisites_met(self):
        """Test prerequisite checking."""
        task = Task(
            title="Test Task",
            prerequisites=["Task 1", "Task 2"]
        )
        
        # No completed tasks
        assert not task.has_prerequisites_met([])
        
        # Partial completion
        assert not task.has_prerequisites_met(["Task 1"])
        
        # All prerequisites met
        assert task.has_prerequisites_met(["Task 1", "Task 2"])
        
        # Extra completed tasks
        assert task.has_prerequisites_met(["Task 1", "Task 2", "Task 3"])
    
    def test_to_markdown_line(self):
        """Test markdown formatting."""
        task = Task(
            title="Test Task",
            number=1,
            description="Task description",
            acceptance_criteria=["Criterion 1", "Criterion 2"],
            requirements_refs=["1.1", "2.3"]
        )
        
        markdown = task.to_markdown_line()
        
        assert "- [ ] 1 Test Task" in markdown
        assert "Task description" in markdown
        assert "Criterion 1" in markdown
        assert "Criterion 2" in markdown
        assert "_Requirements: 1.1, 2.3_" in markdown
    
    def test_to_markdown_line_completed(self):
        """Test markdown formatting for completed task."""
        task = Task(title="Completed Task", number=1, completed=True)
        markdown = task.to_markdown_line()
        assert "- [x] 1 Completed Task" in markdown
    
    def test_to_markdown_line_with_indent(self):
        """Test markdown formatting with indentation."""
        task = Task(title="Subtask", number=1, parent_number=2)
        markdown = task.to_markdown_line(indent_level=1)
        assert markdown.startswith("  - [ ] 2.1 Subtask")


class TestTaskDocument:
    """Test cases for TaskDocument class."""
    
    def test_task_document_creation(self):
        """Test basic task document creation."""
        doc = TaskDocument()
        assert len(doc.tasks) == 0
        assert doc.next_task_number == 1
    
    def test_add_task(self):
        """Test adding tasks to document."""
        doc = TaskDocument()
        task1 = Task(title="Task 1")
        task2 = Task(title="Task 2", number=5)  # Pre-assigned number
        
        doc.add_task(task1)
        doc.add_task(task2)
        
        assert len(doc.tasks) == 2
        assert task1.number == 1
        assert task2.number == 5
        assert doc.next_task_number == 2  # Should increment from auto-assigned
    
    def test_get_task_by_number(self):
        """Test finding tasks by number."""
        doc = TaskDocument()
        main_task = Task(title="Main Task", number=1)
        subtask = Task(title="Subtask", number=1, parent_number=1)
        main_task.add_subtask(subtask)
        doc.add_task(main_task)
        
        # Find main task
        found_main = doc.get_task_by_number("1")
        assert found_main == main_task
        
        # Find subtask
        found_sub = doc.get_task_by_number("1.1")
        assert found_sub == subtask
        
        # Non-existent task
        not_found = doc.get_task_by_number("99")
        assert not_found is None
    
    def test_get_max_task_number(self):
        """Test getting maximum task number."""
        doc = TaskDocument()
        doc.add_task(Task(title="Task 1", number=1))
        doc.add_task(Task(title="Task 3", number=3))
        doc.add_task(Task(title="Task 2", number=2))
        
        assert doc.get_max_task_number() == 3


class TestTaskGenerator:
    """Test cases for TaskGenerator class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.generator = TaskGenerator()
        
        # Sample task suggestions
        self.sample_suggestions = [
            TaskSuggestion(
                title="Set up environment",
                description="Install dependencies and configure environment",
                acceptance_criteria=["Python installed", "Dependencies installed"],
                prerequisites=[],
                estimated_time=30,
                difficulty="easy"
            ),
            TaskSuggestion(
                title="Understand codebase",
                description="Explore and understand the project structure",
                acceptance_criteria=["Can navigate codebase", "Understands main components"],
                prerequisites=["Set up environment"],
                estimated_time=45,
                difficulty="medium"
            ),
            TaskSuggestion(
                title="Run tests",
                description="Execute the test suite",
                acceptance_criteria=["All tests pass", "Understands test structure"],
                prerequisites=["Set up environment"],
                estimated_time=20,
                difficulty="easy"
            )
        ]
    
    def test_generate_onboarding_tasks(self):
        """Test generating onboarding tasks from suggestions."""
        task_doc = self.generator.generate_onboarding_tasks(self.sample_suggestions)
        
        assert isinstance(task_doc, TaskDocument)
        assert len(task_doc.tasks) > 0
        
        # Check that tasks have proper numbering
        for i, task in enumerate(task_doc.tasks):
            assert task.number == i + 1
    
    def test_sort_suggestions_by_priority(self):
        """Test sorting suggestions by priority."""
        # Create suggestions with different priorities
        suggestions = [
            TaskSuggestion(title="Hard Task", difficulty="hard", estimated_time=60, prerequisites=["A", "B"]),
            TaskSuggestion(title="Easy Task", difficulty="easy", estimated_time=15, prerequisites=[]),
            TaskSuggestion(title="Medium Task", difficulty="medium", estimated_time=30, prerequisites=["A"])
        ]
        
        sorted_suggestions = self.generator._sort_suggestions_by_priority(suggestions)
        
        # Easy task should come first (lowest difficulty, no prerequisites, short time)
        assert sorted_suggestions[0].title == "Easy Task"
        assert sorted_suggestions[-1].title == "Hard Task"
    
    def test_group_suggestions_into_tasks(self):
        """Test grouping suggestions into main tasks and subtasks."""
        grouped = self.generator._group_suggestions_into_tasks(self.sample_suggestions)
        
        assert len(grouped) > 0
        for group in grouped:
            assert 'main' in group
            assert 'subtasks' in group
            assert isinstance(group['main'], TaskSuggestion)
            assert isinstance(group['subtasks'], list)
    
    def test_should_be_subtask(self):
        """Test subtask determination logic."""
        main_suggestion = TaskSuggestion(
            title="Set up environment",
            description="Main setup task",
            difficulty="medium"
        )
        
        # Should be subtask - has main as prerequisite
        subtask_candidate = TaskSuggestion(
            title="Install dependencies",
            description="Install project dependencies",
            prerequisites=["Set up environment"],
            difficulty="easy"
        )
        
        assert self.generator._should_be_subtask(main_suggestion, subtask_candidate)
        
        # Should not be subtask - unrelated
        unrelated_candidate = TaskSuggestion(
            title="Write documentation",
            description="Create project documentation",
            difficulty="hard"
        )
        
        assert not self.generator._should_be_subtask(main_suggestion, unrelated_candidate)
    
    def test_create_task_from_suggestion(self):
        """Test creating Task from TaskSuggestion."""
        suggestion = self.sample_suggestions[0]
        task = self.generator._create_task_from_suggestion(suggestion)
        
        assert isinstance(task, Task)
        assert task.title == suggestion.title
        assert task.description == suggestion.description
        assert task.acceptance_criteria == suggestion.acceptance_criteria
        assert task.prerequisites == suggestion.prerequisites
        assert task.estimated_time == suggestion.estimated_time
        assert task.difficulty == suggestion.difficulty
    
    def test_format_tasks_markdown(self):
        """Test formatting tasks as markdown."""
        # Create a simple task document
        doc = TaskDocument()
        main_task = Task(title="Main Task", number=1, description="Main task description")
        subtask = Task(title="Subtask", description="Subtask description")
        main_task.add_subtask(subtask)
        doc.add_task(main_task)
        
        markdown = self.generator.format_tasks_markdown(doc)
        
        assert "# Implementation Plan" in markdown
        assert "- [ ] 1 Main Task" in markdown
        assert "Main task description" in markdown
        assert "- [ ] 1.1 Subtask" in markdown
        assert "Subtask description" in markdown
    
    def test_append_feature_tasks(self):
        """Test appending feature tasks to existing document."""
        # Create existing task document
        existing_doc = TaskDocument()
        existing_task = Task(title="Existing Task", number=1)
        existing_doc.add_task(existing_task)
        
        # Create feature analysis
        feature_analysis = FeatureAnalysis(
            feature_path="features/new_feature.py",
            functions=["new_function", "helper_function"],
            classes=[],
            tests=["test_new_function"],
            documentation="New feature for testing",
            complexity="medium"
        )
        
        # Append feature tasks
        updated_doc = self.generator.append_feature_tasks(feature_analysis, existing_doc)
        
        assert len(updated_doc.tasks) > 1  # Should have more tasks now
        
        # Check that new tasks were added with proper numbering
        task_titles = [task.title for task in updated_doc.tasks]
        assert any("new_feature" in title.lower() for title in task_titles)
    
    def test_generate_feature_task_suggestions(self):
        """Test generating task suggestions for a feature."""
        feature_analysis = FeatureAnalysis(
            feature_path="features/calculator.py",
            functions=["add", "subtract", "multiply"],
            classes=[],
            tests=["test_add", "test_subtract"],
            documentation="Calculator feature",
            complexity="low"
        )
        
        suggestions = self.generator._generate_feature_task_suggestions(feature_analysis)
        
        assert len(suggestions) > 0
        
        # Should have understanding task
        titles = [s.title for s in suggestions]
        assert any("understand" in title.lower() and "calculator" in title.lower() for title in titles)
        
        # Should have test-related task since tests exist
        assert any("test" in title.lower() for title in titles)
    
    def test_find_feature_insertion_point(self):
        """Test finding insertion point for feature tasks."""
        doc = TaskDocument()
        
        # Add setup tasks
        setup_task = Task(title="Set up environment", number=1)
        install_task = Task(title="Install dependencies", number=2)
        feature_task = Task(title="Understand existing features", number=3)
        
        doc.add_task(setup_task)
        doc.add_task(install_task)
        doc.add_task(feature_task)
        
        feature_analysis = FeatureAnalysis(
            feature_path="features/test.py",
            functions=["test_func"],
            classes=[],
            tests=[],
            documentation="",
            complexity="low"
        )
        
        insertion_point = self.generator._find_feature_insertion_point(doc, feature_analysis)
        
        # Should insert after setup tasks (index 2, before "Understand existing features")
        assert insertion_point == 2
    
    def test_resolve_prerequisites(self):
        """Test resolving prerequisites between tasks."""
        doc = TaskDocument()
        
        task1 = Task(title="First Task", number=1)
        task2 = Task(title="Second Task", number=2, prerequisites=["First Task"])
        
        doc.add_task(task1)
        doc.add_task(task2)
        
        self.generator._resolve_prerequisites(doc)
        
        # Prerequisites should be updated with task numbers
        assert "1 First Task" in task2.prerequisites[0]
    
    @patch('src.generators.task_generator.logging.getLogger')
    def test_logging(self, mock_logger):
        """Test that logging is properly configured."""
        generator = TaskGenerator()
        assert generator.logger is not None
    
    def test_error_handling(self):
        """Test error handling in task generation."""
        # Test with invalid suggestions
        invalid_suggestions = [None, "not a suggestion"]
        
        with pytest.raises(Exception):
            self.generator.generate_onboarding_tasks(invalid_suggestions)
    
    def test_empty_suggestions(self):
        """Test handling empty suggestions list."""
        task_doc = self.generator.generate_onboarding_tasks([])
        
        assert isinstance(task_doc, TaskDocument)
        assert len(task_doc.tasks) == 0
    
    def test_complex_prerequisite_chain(self):
        """Test handling complex prerequisite chains."""
        suggestions = [
            TaskSuggestion(title="A", prerequisites=[], difficulty="easy"),
            TaskSuggestion(title="B", prerequisites=["A"], difficulty="easy"),
            TaskSuggestion(title="C", prerequisites=["B"], difficulty="easy"),
            TaskSuggestion(title="D", prerequisites=["A", "C"], difficulty="medium")
        ]
        
        task_doc = self.generator.generate_onboarding_tasks(suggestions)
        
        # Verify tasks were created and prerequisites resolved
        assert len(task_doc.tasks) > 0
        
        # Find task D and verify its prerequisites reference task numbers
        task_d = None
        for task in task_doc.tasks:
            if task.title == "D":
                task_d = task
                break
            for subtask in task.subtasks:
                if subtask.title == "D":
                    task_d = subtask
                    break
        
        if task_d:
            # Prerequisites should contain task numbers
            prereq_text = " ".join(task_d.prerequisites)
            assert any(char.isdigit() for char in prereq_text)


if __name__ == "__main__":
    pytest.main([__file__])