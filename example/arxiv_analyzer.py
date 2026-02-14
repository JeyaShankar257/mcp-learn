import arxiv
import json
import os
from typing import List, Dict, Optional
from dotenv import load_dotenv
import anthropic

# Load environment variables
load_dotenv()


class ArxivAnalyzer:
    """A tool for searching arXiv papers and analyzing them with Claude."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the ArxivAnalyzer.
        
        Args:
            api_key: Anthropic API key. If not provided, reads from ANTHROPIC_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY must be set in environment or passed to constructor")
        
        self.client = anthropic.Anthropic(api_key=self.api_key)
    
    def search_papers(
        self, 
        query: str, 
        max_results: int = 5,
        sort_by: arxiv.SortCriterion = arxiv.SortCriterion.Relevance
    ) -> List[Dict]:
        """
        Search arXiv for papers matching the query.
        
        Args:
            query: Search query (can use arXiv syntax like "cat:cs.AI")
            max_results: Maximum number of results to return
            sort_by: How to sort results (Relevance, LastUpdatedDate, SubmittedDate)
        
        Returns:
            List of paper dictionaries with metadata
        """
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=sort_by
        )
        
        papers = []
        for result in search.results():
            paper = {
                "title": result.title,
                "authors": [author.name for author in result.authors],
                "summary": result.summary,
                "published": result.published.strftime("%Y-%m-%d"),
                "updated": result.updated.strftime("%Y-%m-%d"),
                "arxiv_id": result.entry_id.split("/")[-1],
                "pdf_url": result.pdf_url,
                "categories": result.categories,
                "primary_category": result.primary_category
            }
            papers.append(paper)
        
        return papers
    
    def download_paper(self, arxiv_id: str, download_dir: str = "./papers") -> str:
        """
        Download a paper PDF from arXiv.
        
        Args:
            arxiv_id: arXiv paper ID (e.g., "2301.12345")
            download_dir: Directory to save the PDF
        
        Returns:
            Path to the downloaded PDF
        """
        os.makedirs(download_dir, exist_ok=True)
        
        search = arxiv.Search(id_list=[arxiv_id])
        paper = next(search.results())
        
        filepath = paper.download_pdf(dirpath=download_dir)
        return filepath
    
    def analyze_paper(
        self, 
        paper: Dict, 
        analysis_type: str = "summary",
        custom_prompt: Optional[str] = None
    ) -> str:
        """
        Analyze a paper using Claude.
        
        Args:
            paper: Paper dictionary from search_papers()
            analysis_type: Type of analysis - "summary", "key_findings", "methodology", "critique"
            custom_prompt: Custom analysis prompt (overrides analysis_type)
        
        Returns:
            Claude's analysis as a string
        """
        # Prepare the paper content
        paper_content = f"""
Title: {paper['title']}

Authors: {', '.join(paper['authors'])}

Published: {paper['published']}

Categories: {', '.join(paper['categories'])}

Abstract:
{paper['summary']}
"""
        
        # Define analysis prompts
        prompts = {
            "summary": "Please provide a concise summary of this paper, highlighting the main contributions and findings.",
            "key_findings": "What are the key findings and contributions of this paper? List them clearly.",
            "methodology": "Analyze the methodology used in this paper. What approaches did the authors take?",
            "critique": "Provide a balanced critique of this paper, discussing both strengths and potential limitations."
        }
        
        analysis_prompt = custom_prompt or prompts.get(analysis_type, prompts["summary"])
        
        # Create the full prompt
        full_prompt = f"{paper_content}\n\n{analysis_prompt}"
        
        # Call Claude API
        message = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[
                {"role": "user", "content": full_prompt}
            ]
        )
        
        return message.content[0].text
    
    def batch_analyze_papers(
        self, 
        papers: List[Dict], 
        analysis_type: str = "summary"
    ) -> List[Dict]:
        """
        Analyze multiple papers and return results.
        
        Args:
            papers: List of paper dictionaries
            analysis_type: Type of analysis to perform on each paper
        
        Returns:
            List of papers with added "analysis" field
        """
        analyzed_papers = []
        
        for paper in papers:
            print(f"Analyzing: {paper['title'][:60]}...")
            analysis = self.analyze_paper(paper, analysis_type)
            
            analyzed_paper = paper.copy()
            analyzed_paper["analysis"] = analysis
            analyzed_papers.append(analyzed_paper)
        
        return analyzed_papers
    
    def compare_papers(self, papers: List[Dict]) -> str:
        """
        Compare multiple papers and identify common themes and differences.
        
        Args:
            papers: List of paper dictionaries (2-5 papers recommended)
        
        Returns:
            Comparative analysis from Claude
        """
        if len(papers) < 2:
            raise ValueError("Need at least 2 papers to compare")
        
        # Prepare papers for comparison
        papers_text = ""
        for i, paper in enumerate(papers, 1):
            papers_text += f"""
Paper {i}:
Title: {paper['title']}
Authors: {', '.join(paper['authors'])}
Abstract: {paper['summary']}

---
"""
        
        prompt = f"""Here are {len(papers)} research papers. Please compare them by:

1. Identifying common themes and research directions
2. Highlighting key differences in approach or findings
3. Discussing how these papers relate to each other
4. Noting any complementary or contradictory findings

Papers:
{papers_text}

Please provide a comparative analysis:"""
        
        message = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=3000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        return message.content[0].text
    
    def save_results(self, data: List[Dict], filename: str = "arxiv_results.json"):
        """Save analysis results to a JSON file."""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Results saved to {filename}")


def main():
    """Example usage of the ArxivAnalyzer."""
    
    # Initialize the analyzer
    analyzer = ArxivAnalyzer()
    
    # Example 1: Search for papers on a topic
    print("=" * 80)
    print("Searching for papers on 'large language models'...")
    print("=" * 80)
    papers = analyzer.search_papers(
        query="large language models",
        max_results=3
    )
    
    print(f"\nFound {len(papers)} papers:\n")
    for i, paper in enumerate(papers, 1):
        print(f"{i}. {paper['title']}")
        print(f"   Authors: {', '.join(paper['authors'][:3])}{'...' if len(paper['authors']) > 3 else ''}")
        print(f"   Published: {paper['published']}")
        print(f"   ID: {paper['arxiv_id']}\n")
    
    # Example 2: Analyze a single paper
    if papers:
        print("=" * 80)
        print(f"Analyzing first paper...")
        print("=" * 80)
        analysis = analyzer.analyze_paper(papers[0], analysis_type="summary")
        print(f"\nAnalysis:\n{analysis}\n")
    
    # Example 3: Batch analyze multiple papers
    print("=" * 80)
    print("Performing batch analysis...")
    print("=" * 80)
    analyzed_papers = analyzer.batch_analyze_papers(papers, analysis_type="key_findings")
    
    # Example 4: Compare papers
    if len(papers) >= 2:
        print("=" * 80)
        print("Comparing papers...")
        print("=" * 80)
        comparison = analyzer.compare_papers(papers[:2])
        print(f"\nComparative Analysis:\n{comparison}\n")
    
    # Example 5: Save results
    analyzer.save_results(analyzed_papers, "arxiv_analysis_results.json")
    
    # Example 6: Download a paper (commented out to avoid downloads in demo)
    # pdf_path = analyzer.download_paper(papers[0]['arxiv_id'])
    # print(f"Downloaded paper to: {pdf_path}")


if __name__ == "__main__":
    main()
