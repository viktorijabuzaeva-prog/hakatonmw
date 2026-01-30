"""
Insights Manager Module
Manages the master insights database and individual reports
"""
import os
import re
from typing import Dict, List, Optional
from datetime import datetime


class InsightsManager:
    """Manage insights storage and updates"""
    
    def __init__(
        self, 
        insights_dir: str = "Insights",
        master_file: str = "master_insights.md",
        reports_dir: str = "reports"
    ):
        self.insights_dir = insights_dir
        self.master_file_path = os.path.join(insights_dir, master_file)
        self.reports_dir = os.path.join(insights_dir, reports_dir)
        
        # Create directories if they don't exist
        os.makedirs(self.insights_dir, exist_ok=True)
        os.makedirs(self.reports_dir, exist_ok=True)
    
    def load_master_insights(self) -> str:
        """
        Load the master insights file
        
        Returns:
            Content of master_insights.md as string
        """
        try:
            if os.path.exists(self.master_file_path):
                with open(self.master_file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                return self._create_default_master_insights()
        except Exception as e:
            print(f"Error loading master insights: {e}")
            return ""
    
    def _create_default_master_insights(self) -> str:
        """Create default master insights file"""
        default_content = """# Накопленные инсайты из интервью

## Метаданные
- Всего проанализировано интервью: 0
- Последнее обновление: не проводилось
- Дата создания базы: {date}

## Ключевые темы

_Темы будут добавлены после первичного анализа транскриптов_

## Паттерны поведения

_Паттерны будут выявлены после анализа_

## Боли пользователей

_Боли будут идентифицированы после анализа_

## Рекомендации для следующих интервью

_Рекомендации будут сформированы на основе накопленных данных_
""".format(date=datetime.now().strftime('%Y-%m-%d'))
        
        # Save default file
        with open(self.master_file_path, 'w', encoding='utf-8') as f:
            f.write(default_content)
        
        return default_content
    
    def save_master_insights(self, content: str) -> bool:
        """
        Save content to master insights file
        
        Args:
            content: Full content to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.master_file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"Error saving master insights: {e}")
            return False
    
    def save_individual_report(
        self, 
        respondent_name: str, 
        analysis: str,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Save an individual analysis report
        
        Args:
            respondent_name: Name of respondent
            analysis: Full analysis text
            metadata: Optional metadata dictionary
            
        Returns:
            Path to saved report
        """
        # Create safe filename
        safe_name = re.sub(r'[^\w\s-]', '', respondent_name).strip()
        safe_name = re.sub(r'[-\s]+', '-', safe_name)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{safe_name}_{timestamp}.md"
        filepath = os.path.join(self.reports_dir, filename)
        
        # Build report with metadata header
        report_content = f"""# Анализ интервью: {respondent_name}

## Метаданные
- Респондент: {respondent_name}
- Дата анализа: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        if metadata:
            for key, value in metadata.items():
                report_content += f"- {key}: {value}\n"
        
        report_content += f"\n---\n\n{analysis}\n"
        
        # Save report
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(report_content)
            return filepath
        except Exception as e:
            print(f"Error saving report: {e}")
            return ""
    
    def update_master_insights(
        self, 
        new_analysis: str,
        respondent_name: str,
        transcript_number: int
    ) -> bool:
        """
        Update master insights with new analysis
        
        Args:
            new_analysis: New analysis text
            respondent_name: Name of respondent
            transcript_number: Current transcript count
            
        Returns:
            True if successful
        """
        try:
            # Load existing insights
            master_content = self.load_master_insights()
            
            # Update metadata
            master_content = self._update_metadata(
                master_content, 
                transcript_number
            )
            
            # Extract and merge insights
            merged_content = self._merge_insights(
                master_content,
                new_analysis,
                respondent_name
            )
            
            # Save updated master
            return self.save_master_insights(merged_content)
            
        except Exception as e:
            print(f"Error updating master insights: {e}")
            return False
    
    def _update_metadata(self, content: str, count: int) -> str:
        """Update metadata section with new count and date"""
        # Update interview count
        content = re.sub(
            r'Всего проанализировано интервью: \d+',
            f'Всего проанализировано интервью: {count}',
            content
        )
        
        # Update last update date
        today = datetime.now().strftime('%Y-%m-%d')
        content = re.sub(
            r'Последнее обновление: .*',
            f'Последнее обновление: {today}',
            content
        )
        
        return content
    
    def _merge_insights(
        self, 
        master_content: str, 
        new_analysis: str,
        respondent_name: str
    ) -> str:
        """
        Merge new analysis into master insights
        
        This is a simplified version - in production, you'd want more
        sophisticated merging logic that intelligently combines themes
        """
        # For now, append new insights to the end
        separator = f"\n\n---\n\n## Инсайты из интервью: {respondent_name}\n"
        separator += f"_Дата добавления: {datetime.now().strftime('%Y-%m-%d')}_\n\n"
        
        merged = master_content + separator + new_analysis
        
        return merged
    
    def extract_tags_from_analysis(self, analysis: str) -> List[str]:
        """
        Extract hashtags from analysis text
        
        Args:
            analysis: Analysis text containing hashtags
            
        Returns:
            List of unique tags
        """
        # Find all hashtags
        tags = re.findall(r'#\w+', analysis)
        
        # Return unique tags, preserving order
        seen = set()
        unique_tags = []
        for tag in tags:
            if tag.lower() not in seen:
                seen.add(tag.lower())
                unique_tags.append(tag)
        
        return unique_tags
    
    def get_statistics(self) -> Dict[str, any]:
        """
        Get statistics about the insights database
        
        Returns:
            Dictionary with statistics
        """
        master_content = self.load_master_insights()
        
        # Extract interview count
        count_match = re.search(r'Всего проанализировано интервью: (\d+)', master_content)
        interview_count = int(count_match.group(1)) if count_match else 0
        
        # Extract last update date
        date_match = re.search(r'Последнее обновление: (.+)', master_content)
        last_update = date_match.group(1) if date_match else "не проводилось"
        
        # Count individual reports
        report_files = [f for f in os.listdir(self.reports_dir) if f.endswith('.md')]
        report_count = len(report_files)
        
        # Extract all tags
        all_tags = self.extract_tags_from_analysis(master_content)
        
        return {
            'total_interviews': interview_count,
            'last_update': last_update,
            'report_count': report_count,
            'unique_tags': len(set(t.lower() for t in all_tags)),
            'tags': all_tags,
            'master_file_size': os.path.getsize(self.master_file_path) if os.path.exists(self.master_file_path) else 0
        }
    
    def search_insights(self, query: str) -> List[Dict[str, any]]:
        """
        Search through master insights and reports
        
        Args:
            query: Search query
            
        Returns:
            List of matching results
        """
        results = []
        query_lower = query.lower()
        
        # Search in master insights
        master_content = self.load_master_insights()
        if query_lower in master_content.lower():
            # Find context around matches
            lines = master_content.split('\n')
            for i, line in enumerate(lines):
                if query_lower in line.lower():
                    context_start = max(0, i - 2)
                    context_end = min(len(lines), i + 3)
                    context = '\n'.join(lines[context_start:context_end])
                    
                    results.append({
                        'source': 'master_insights.md',
                        'line_number': i + 1,
                        'context': context
                    })
        
        # Search in individual reports
        for filename in os.listdir(self.reports_dir):
            if filename.endswith('.md'):
                filepath = os.path.join(self.reports_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if query_lower in content.lower():
                        # Extract respondent name from filename
                        respondent = filename.replace('.md', '').rsplit('_', 2)[0]
                        
                        results.append({
                            'source': filename,
                            'respondent': respondent,
                            'matched': True
                        })
                except Exception as e:
                    print(f"Error searching {filename}: {e}")
        
        return results
    
    def list_reports(self) -> List[Dict[str, str]]:
        """
        List all individual reports
        
        Returns:
            List of report metadata
        """
        reports = []
        
        for filename in os.listdir(self.reports_dir):
            if filename.endswith('.md') and filename != '.gitkeep':
                filepath = os.path.join(self.reports_dir, filename)
                stats = os.stat(filepath)
                
                # Extract respondent name from filename
                respondent = filename.replace('.md', '').rsplit('_', 2)[0]
                
                reports.append({
                    'filename': filename,
                    'respondent': respondent,
                    'path': filepath,
                    'size': stats.st_size,
                    'modified': datetime.fromtimestamp(stats.st_mtime).isoformat()
                })
        
        # Sort by modified date (newest first)
        reports.sort(key=lambda x: x['modified'], reverse=True)
        
        return reports
    
    def load_report(self, respondent_name: str) -> Optional[str]:
        """
        Load a specific report by respondent name
        
        Args:
            respondent_name: Name of respondent (without extension)
            
        Returns:
            Report content as string, or None if not found
        """
        try:
            # Search for report file matching respondent name
            for filename in os.listdir(self.reports_dir):
                if filename.endswith('.md'):
                    # Extract respondent name from filename
                    file_respondent = filename.replace('.md', '').rsplit('_', 2)[0]
                    
                    if file_respondent.lower() == respondent_name.lower().replace(' ', '-'):
                        filepath = os.path.join(self.reports_dir, filename)
                        with open(filepath, 'r', encoding='utf-8') as f:
                            return f.read()
            
            return None
        except Exception as e:
            print(f"Error loading report for {respondent_name}: {e}")
            return None


def test_insights_manager():
    """Test function"""
    print("=== Testing Insights Manager ===\n")
    
    manager = InsightsManager()
    
    # Load master insights
    master = manager.load_master_insights()
    print(f"Master insights loaded: {len(master)} characters\n")
    
    # Get statistics
    stats = manager.get_statistics()
    print("Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Test saving a report
    test_analysis = """## Краткое резюме
Пользователь испытывает трудности с авторизацией

## Боли
- Долгий вход в приложение
- Нет возможности сохранить сессию

## Теги
#mobile_app #authentication #usability
"""
    
    report_path = manager.save_individual_report(
        "Тестовый Пользователь",
        test_analysis,
        {'word_count': 150}
    )
    
    if report_path:
        print(f"\n✅ Test report saved: {report_path}")


if __name__ == "__main__":
    test_insights_manager()
