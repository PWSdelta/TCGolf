# Golf Content Generation System

This system helps you generate comprehensive golf destination articles using LLM chains.

## Setup

1. **Install Dependencies** (if needed):
   ```bash
   pip install requests
   ```

2. **Set API Key** (optional, will use mock data without it):
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```
   Or pass it directly: `--api-key your-key`

## Single Destination Generation

### Generate everything for one destination:
```bash
python content_generator.py --destination "Tokyo, Tokyo, Japan" --all
```

### Step-by-step generation:
```bash
# 1. Generate topics
python content_generator.py --destination "Tokyo, Tokyo, Japan" --generate-topics

# 2. Generate article from topics
python content_generator.py --destination "Tokyo, Tokyo, Japan" --generate-article

# 3. Upload to database
python content_generator.py --destination "Tokyo, Tokyo, Japan" --upload
```

## Batch Processing

### Generate all destinations from list:
```bash
python batch_generator.py --input international_destinations.txt --all
```

### Generate only topics for all destinations (faster, cheaper):
```bash
python batch_generator.py --input international_destinations.txt --generate-topics-only
```

### Options for batch processing:
```bash
# Start from a specific destination (useful if interrupted)
python batch_generator.py --input international_destinations.txt --all --start-from 10

# Add delay between requests (be nice to APIs)
python batch_generator.py --input international_destinations.txt --all --delay 5

# Use different API key
python batch_generator.py --input international_destinations.txt --all --api-key your-key
```

## File Structure

After running, you'll have:
```
generated_content/
├── Tokyo_Tokyo_Japan_topics.txt      # Generated topics
├── Tokyo_Tokyo_Japan_article.md      # Generated article
├── Seoul_Seoul_South_Korea_topics.txt
├── Seoul_Seoul_South_Korea_article.md
└── ...
```

## Custom Destination Lists

Create your own list file:
```
# my_destinations.txt
Barcelona, Catalonia, Spain
Nice, Provence-Alpes-Côte d'Azur, France
Dublin, Dublin, Ireland
```

Then run:
```bash
python batch_generator.py --input my_destinations.txt --all
```

## API Usage & Costs

- **Topics Generation**: ~500 tokens per destination ($0.01-0.02 each)
- **Article Generation**: ~4000 tokens per destination ($0.08-0.15 each)
- **Total per destination**: ~$0.10-0.20 with GPT-3.5-turbo

For 100 destinations: ~$10-20 total

## Tips

1. **Start Small**: Test with 5-10 destinations first
2. **Use Topics-Only**: Generate topics for all destinations first, review quality
3. **Batch Processing**: Use delays between requests to avoid rate limits
4. **Review Content**: Always review generated articles before uploading
5. **Backup**: Content is saved to files before database upload

## Error Handling

- Failed destinations are saved to `failed_destinations.txt`
- You can retry failed ones: `python batch_generator.py --input failed_destinations.txt --all`
- Timeouts are set to 5 minutes per destination
- All generated content is saved to files as backup

## Database Integration

The system automatically:
- ✅ Gets coordinates via geocoding
- ✅ Handles duplicate destinations (updates existing)
- ✅ Generates SEO-friendly slugs
- ✅ Creates proper URLs
- ✅ Integrates with existing Django models
