# arXiv Paper Analyzer with Claude

A Python tool for searching arXiv papers and analyzing them using Claude AI.

## Features

- 🔍 **Search arXiv papers** by topic, author, or category
- 📄 **Extract paper metadata** (title, authors, abstract, dates, categories)
- 🤖 **AI-powered analysis** using Claude to summarize and analyze papers
- 📊 **Batch processing** to analyze multiple papers at once
- 🔄 **Compare papers** to find common themes and differences
- 💾 **Download PDFs** directly from arXiv
- 📁 **Save results** to JSON for later use

## Installation

1. Clone or download this repository

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your API key:
   - Copy `.env.example` to `.env`
   - Add your Anthropic API key to the `.env` file:
   ```
   ANTHROPIC_API_KEY=your_actual_api_key_here
   ```

## Quick Start

Run the example script:
```bash
python arxiv_analyzer.py
```

This will search for papers on "large language models", analyze them, and save results.

## Usage Examples

### Basic Search

```python
from arxiv_analyzer import ArxivAnalyzer

# Initialize
analyzer = ArxivAnalyzer()

# Search for papers
papers = analyzer.search_papers(
    query="neural networks",
    max_results=5
)

# Print results
for paper in papers:
    print(f"Title: {paper['title']}")
    print(f"Authors: {', '.join(paper['authors'])}")
    print(f"Published: {paper['published']}\n")
```

### Advanced Search Queries

```python
# Search by category
papers = analyzer.search_papers(
    query="cat:cs.AI",  # Computer Science - AI
    max_results=10
)

# Search by author
papers = analyzer.search_papers(
    query="au:Hinton",
    max_results=5
)

# Combined search
papers = analyzer.search_papers(
    query="cat:cs.LG AND attention mechanism",
    max_results=5
)

# Sort by date
import arxiv
papers = analyzer.search_papers(
    query="transformers",
    max_results=5,
    sort_by=arxiv.SortCriterion.SubmittedDate
)
```

### Analyze a Single Paper

```python
# Get papers
papers = analyzer.search_papers("quantum computing", max_results=1)

# Different types of analysis
summary = analyzer.analyze_paper(papers[0], analysis_type="summary")
findings = analyzer.analyze_paper(papers[0], analysis_type="key_findings")
methodology = analyzer.analyze_paper(papers[0], analysis_type="methodology")
critique = analyzer.analyze_paper(papers[0], analysis_type="critique")

print(summary)
```

### Custom Analysis Prompt

```python
custom_analysis = analyzer.analyze_paper(
    papers[0],
    custom_prompt="Explain this paper's contribution in simple terms for a general audience."
)
```

### Batch Analysis

```python
# Search and analyze multiple papers
papers = analyzer.search_papers("machine learning", max_results=5)

# Analyze all papers
analyzed_papers = analyzer.batch_analyze_papers(
    papers, 
    analysis_type="key_findings"
)

# Access results
for paper in analyzed_papers:
    print(f"\nPaper: {paper['title']}")
    print(f"Analysis: {paper['analysis']}")
```

### Compare Papers

```python
# Get papers on a topic
papers = analyzer.search_papers("reinforcement learning", max_results=3)

# Compare them
comparison = analyzer.compare_papers(papers)
print(comparison)
```

### Download Papers

```python
# Download a paper PDF
papers = analyzer.search_papers("attention is all you need", max_results=1)
pdf_path = analyzer.download_paper(
    papers[0]['arxiv_id'],
    download_dir="./my_papers"
)
print(f"Downloaded to: {pdf_path}")
```

### Save Results

```python
# Save analyzed papers to JSON
analyzed_papers = analyzer.batch_analyze_papers(papers)
analyzer.save_results(analyzed_papers, "my_analysis.json")

# Load results later
import json
with open("my_analysis.json", 'r') as f:
    loaded_papers = json.load(f)
```

## Complete Workflow Example

```python
from arxiv_analyzer import ArxivAnalyzer

# Initialize
analyzer = ArxivAnalyzer()

# 1. Search for recent papers on a topic
papers = analyzer.search_papers(
    query="cat:cs.AI AND deep learning",
    max_results=10,
    sort_by=arxiv.SortCriterion.SubmittedDate
)

print(f"Found {len(papers)} papers")

# 2. Filter papers by date or criteria
recent_papers = [p for p in papers if p['published'] >= '2024-01-01']

# 3. Analyze the papers
analyzed = analyzer.batch_analyze_papers(
    recent_papers[:5],  # Analyze top 5
    analysis_type="key_findings"
)

# 4. Compare the papers
if len(recent_papers) >= 2:
    comparison = analyzer.compare_papers(recent_papers[:3])
    print("\nComparative Analysis:")
    print(comparison)

# 5. Save everything
analyzer.save_results(analyzed, "ai_papers_analysis.json")

# 6. Download interesting papers
for paper in analyzed[:2]:  # Download top 2
    pdf_path = analyzer.download_paper(
        paper['arxiv_id'],
        download_dir="./downloaded_papers"
    )
    print(f"Downloaded: {pdf_path}")
```

## arXiv Query Syntax

The arXiv API supports various search operators:

- `AND`, `OR`, `ANDNOT` - Boolean operators
- `au:author_name` - Search by author
- `ti:title_words` - Search in title
- `abs:abstract_words` - Search in abstract
- `cat:category` - Search by category
- `all:keywords` - Search all fields

### Common Categories

- `cs.AI` - Artificial Intelligence
- `cs.LG` - Machine Learning
- `cs.CL` - Computation and Language
- `cs.CV` - Computer Vision
- `stat.ML` - Machine Learning (Statistics)
- `math.OC` - Optimization and Control
- `q-bio` - Quantitative Biology
- `physics` - Physics

### Example Queries

```python
# Papers about transformers in NLP
papers = analyzer.search_papers("cat:cs.CL AND transformers")

# Papers by specific author on topic
papers = analyzer.search_papers("au:Bengio AND deep learning")

# Recent papers in AI
papers = analyzer.search_papers("cat:cs.AI", sort_by=arxiv.SortCriterion.SubmittedDate)
```

## API Reference

### `ArxivAnalyzer` Class

#### `__init__(api_key=None)`
Initialize the analyzer with optional API key.

#### `search_papers(query, max_results=5, sort_by=arxiv.SortCriterion.Relevance)`
Search arXiv for papers.

**Returns:** List of paper dictionaries with fields:
- `title`: Paper title
- `authors`: List of author names
- `summary`: Abstract
- `published`: Publication date
- `updated`: Last update date
- `arxiv_id`: arXiv identifier
- `pdf_url`: Direct PDF link
- `categories`: List of arXiv categories
- `primary_category`: Main category

#### `analyze_paper(paper, analysis_type="summary", custom_prompt=None)`
Analyze a single paper with Claude.

**Analysis types:**
- `"summary"` - General summary
- `"key_findings"` - Main findings
- `"methodology"` - Methods analysis
- `"critique"` - Critical analysis

#### `batch_analyze_papers(papers, analysis_type="summary")`
Analyze multiple papers and add "analysis" field to each.

#### `compare_papers(papers)`
Compare 2+ papers to find themes and differences.

#### `download_paper(arxiv_id, download_dir="./papers")`
Download paper PDF. Returns file path.

#### `save_results(data, filename="arxiv_results.json")`
Save analysis results to JSON file.

## Tips

1. **Rate limiting**: The arXiv API has rate limits. For large batches, add delays between requests.

2. **Token usage**: Each analysis uses Claude API tokens. Monitor usage for cost control.

3. **Paper selection**: Start with fewer papers and refine your search before batch processing.

4. **Custom prompts**: Use custom prompts for specialized analysis needs.

5. **Save intermediately**: Save results periodically when processing many papers.

## Troubleshooting

**"ANTHROPIC_API_KEY must be set"**
- Make sure you've created a `.env` file with your API key
- Or pass the key directly: `ArxivAnalyzer(api_key="your-key")`

**No papers found**
- Check your query syntax
- Try broader search terms
- Verify the category exists

**API errors**
- Check your API key is valid
- Ensure you have credits available
- Check network connection

## License

MIT License - feel free to use and modify as needed.

## Contributing

Contributions welcome! Feel free to submit issues or pull requests.
