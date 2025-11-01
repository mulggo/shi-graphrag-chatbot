#!/usr/bin/env python3
import boto3
import json

def retrieve_from_knowledge_base():
    client = boto3.client('bedrock-agent-runtime', region_name='us-west-2')
    
    try:
        # Knowledge Base에서 직접 검색
        response = client.retrieve(
            knowledgeBaseId='ZGBA1R5CS0',
            retrievalQuery={
                'text': 'firefighting 고정식 소화 시스템'
            },
            retrievalConfiguration={
                'vectorSearchConfiguration': {
                    'numberOfResults': 3
                }
            }
        )
        
        print("=== KNOWLEDGE BASE RETRIEVAL RESULTS ===")
        
        if 'retrievalResults' in response:
            results = response['retrievalResults']
            print(f"Found {len(results)} results")
            
            for i, result in enumerate(results, 1):
                print(f"\n--- Result {i} ---")
                print(f"Score: {result.get('score', 'N/A')}")
                
                if 'content' in result:
                    content = result['content']
                    print(f"Content type: {content.get('type', 'unknown')}")
                    
                    if 'text' in content:
                        text = content['text']
                        print(f"Text length: {len(text)} characters")
                        print(f"Text preview (first 500 chars):")
                        print(f"{text[:500]}...")
                    else:
                        print("No text content found")
                
                if 'location' in result:
                    location = result['location']
                    print(f"Location type: {location.get('type', 'unknown')}")
                    if 's3Location' in location:
                        s3_loc = location['s3Location']
                        print(f"S3 URI: {s3_loc.get('uri', 'N/A')}")
                
                if 'metadata' in result:
                    metadata = result['metadata']
                    print(f"Metadata keys: {list(metadata.keys())}")
                    if 'x-amz-bedrock-kb-source-uri' in metadata:
                        print(f"Source: {metadata['x-amz-bedrock-kb-source-uri']}")
                    if 'x-amz-bedrock-kb-document-page-number' in metadata:
                        print(f"Page: {metadata['x-amz-bedrock-kb-document-page-number']}")
                    if 'x-amz-bedrock-kb-description' in metadata:
                        description = metadata['x-amz-bedrock-kb-description']
                        print(f"\n*** OCR EXTRACTED TEXT (first 800 chars) ***")
                        print(f"{description[:800]}...")
                        print(f"Total description length: {len(description)} characters")
                    if 'x-amz-bedrock-kb-byte-content-source' in metadata:
                        image_uri = metadata['x-amz-bedrock-kb-byte-content-source']
                        print(f"\n*** ORIGINAL IMAGE S3 URI ***")
                        print(f"{image_uri}")
                
                print("-" * 60)
        else:
            print("No retrieval results found")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    retrieve_from_knowledge_base()