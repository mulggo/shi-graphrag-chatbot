"""
Plan-Execute Agent - AWS IDP 패턴 기반 150줄 구현
"""

import boto3
import json
import time
from typing import Dict, Any

class PlanExecuteAgent:
    """150줄 목표 Plan-Execute 에이전트 (MD 가이드 Phase 2)"""
    
    def __init__(self, config=None, kb_id=None):
        self.config = config
        self.kb_id = kb_id or "PWRU19RDNE"  # 멀티모달 Knowledge Base ID
        self.bedrock_client = boto3.client('bedrock-agent-runtime', region_name='us-west-2')
        self.bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-west-2')
        self.dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
        self.ocr_table_name = 'ship-firefighting-ocr'
        
        # 실제 Neptune KB의 11개 문서 (S3 버킷 기반)
        self.SHIP_DOCUMENTS = [
            # DNV 규정 (2개)
            "DNV-RU-SHIP-Pt4 Ch6 (Fire Safety Systems)",
            "DNV-RU-SHIP-Pt6 Ch5 Sec4 (Safety Equipment)",
            # 설계 가이드 (3개)
            "Design guidance - Spoolcutting",
            "Design guidance - Support Systems", 
            "Design guidance - Hull Penetration",
            # FSS/SOLAS/IGC 규정 (4개)
            "SOLAS Chapter II-2 (Fire Protection & Detection)",
            "FSS Code (Fire Safety Systems)",
            "IGC Code (Gas Carrier Safety)",
            "SOLAS Insulation Penetration Guidelines",
            # 배관 실무 (2개)
            "Piping Practice - Support Systems",
            "Piping Practice - Hull Penetration"
        ]
    
    def process_message(self, message: str, session_id: str) -> Dict[str, Any]:
        """2단계 워크플로우: Plan+Execute → Rerank+Respond"""
        start_time = time.time()
        
        try:
            # Stage 1: Plan + Execute
            plan = self._create_document_plan(message)
            search_results = self._execute_neptune_search(plan["english_query"])
            
            # Stage 2: Rerank + Respond  
            final_response = self._synthesize_response(message, search_results)
            
            return {
                "success": True,
                "content": final_response["text"],
                "references": final_response["references"],
                "response_time": time.time() - start_time,
                "agent_type": "plan_execute"
            }
            
        except Exception as e:
            return {
                "success": False,
                "content": f"오류: {str(e)}",
                "references": [],
                "agent_type": "plan_execute"
            }
    
    def _create_document_plan(self, query: str) -> Dict:
        """문서 분석 및 검색 계획 수립"""
        prompt = f"""
한국어 질문: "{query}"

11개 선박 규정 문서:
{chr(10).join([f"{i+1}. {doc}" for i, doc in enumerate(self.SHIP_DOCUMENTS)])}

작업: 질문과 관련된 문서들을 선택하고 영어 검색 쿼리를 생성하세요.
(필요에 따라 여러 문서 선택 가능)

JSON 형식:
{{
    "selected_documents": ["관련 문서들"],
    "english_query": "영어 검색 쿼리",
    "reasoning": "문서 선택 이유"
}}
"""
        
        try:
            response = self.bedrock_runtime.invoke_model(
                modelId='anthropic.claude-3-haiku-20240307-v1:0',
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 500,
                    "messages": [{"role": "user", "content": prompt}]
                })
            )
            
            result = json.loads(response['body'].read())
            content = result['content'][0]['text']
            
            try:
                plan_data = json.loads(content)
                return {
                    "success": True,
                    "target_documents": plan_data.get("selected_documents", []),
                    "english_query": plan_data.get("english_query", query)
                }
            except:
                return {
                    "success": True,
                    "target_documents": ["SOLAS Chapter II-2 (Fire Protection)"],
                    "english_query": query
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "target_documents": [],
                "english_query": query
            }
    
    def _execute_neptune_search(self, query: str, kb_id: str = None) -> list:
        """Neptune Analytics KB 검색 실행"""
        try:
            actual_kb_id = kb_id or self.kb_id
            response = self.bedrock_client.retrieve(
                knowledgeBaseId=actual_kb_id,
                retrievalQuery={'text': query},
                retrievalConfiguration={
                    'vectorSearchConfiguration': {
                        'numberOfResults': 10
                    }
                }
            )
            
            results = []
            for result in response['retrievalResults']:
                metadata = result.get('metadata', {})
                content_text = result.get('content', {}).get('text', '')
                
                # 메타데이터에서 상세 정보 추출
                source_uri = metadata.get('x-amz-bedrock-kb-source-uri', '')
                source_file = source_uri.split('/')[-1] if source_uri else 'Unknown'
                
                # KB별 OCR 텍스트 처리
                if actual_kb_id == 'CDPB5AI6BH':
                    # CDPB5AI6BH: description 메타데이터에서 OCR 텍스트
                    ocr_text = metadata.get('x-amz-bedrock-kb-description', content_text)
                elif actual_kb_id == 'PWRU19RDNE':
                    # PWRU19RDNE: DynamoDB에서 실제 OCR 텍스트 조회
                    page_number = metadata.get('x-amz-bedrock-kb-document-page-number')
                    document_id = self._extract_document_id_from_source(source_uri)
                    ocr_text = self._get_ocr_from_dynamodb(document_id, str(int(page_number)) if page_number else '1')
                    if not ocr_text:
                        ocr_text = content_text  # 폴백
                else:
                    ocr_text = content_text
                
                # 이미지 URI 설정 - DynamoDB 기반 정확한 페이지 이미지
                data_source_id = metadata.get('x-amz-bedrock-kb-data-source-id', '')
                
                if actual_kb_id == 'PWRU19RDNE':
                    # PWRU19RDNE: DynamoDB에서 정확한 페이지 이미지 URL 가져오기
                    page_number = metadata.get('x-amz-bedrock-kb-document-page-number')
                    document_id = self._extract_document_id_from_source(source_uri)
                    
                    if page_number and document_id:
                        # DynamoDB에서 정확한 이미지 URL 조회
                        image_uri = self._get_image_url_from_dynamodb(document_id, str(int(page_number)))
                        has_images = bool(image_uri)
                    else:
                        image_uri = ''
                        has_images = False
                elif actual_kb_id == 'CDPB5AI6BH':
                    # CDPB5AI6BH: 기존 방식
                    image_uri = metadata.get('x-amz-bedrock-kb-byte-content-source', '')
                    has_images = bool(image_uri)
                else:
                    image_uri = ''
                    has_images = False
                
                # 페이지 번호
                page_number = int(metadata.get('x-amz-bedrock-kb-document-page-number', 1))
                
                # CDPB5AI6BH KB의 페이지 번호 보정 (1 추가)
                if actual_kb_id == 'CDPB5AI6BH':
                    page_number = page_number + 1
                
                results.append({
                    'content': ocr_text,  # OCR 텍스트 사용
                    'source': source_file,
                    'score': result.get('score', 0.0),
                    # UI 호환성을 위한 추가 필드
                    'source_file': source_file,
                    'page_number': page_number,
                    'ocr_text': ocr_text,
                    'image_uri': image_uri,
                    'has_multimodal': has_images,
                    'data_source_id': data_source_id,
                    'metadata': metadata
                })
            
            return results
            
        except Exception as e:
            return []
    
    def _synthesize_response(self, query: str, documents: list) -> Dict:
        """Cohere Reranking + 한국어 응답 합성"""
        if not documents:
            return {
                "text": "관련 문서를 찾지 못했습니다.",
                "references": []
            }
        
        # Cohere Reranking 실행
        reranked_docs = self._cohere_rerank(query, documents)
        
        # 상위 5개 문서로 컨텍스트 구성
        context = "\n\n".join([f"[문서 {i+1}] {doc['content'][:300]}..." 
                              for i, doc in enumerate(reranked_docs[:5])])
        
        # 한국어 응답 생성
        prompt = f"""
질문: {query}

관련 문서:
{context}

위 문서들을 바탕으로 질문에 대한 정확하고 상세한 한국어 답변을 작성하세요.
"""
        
        try:
            response = self.bedrock_runtime.invoke_model(
                modelId='anthropic.claude-3-sonnet-20240229-v1:0',
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 1500,
                    "messages": [{"role": "user", "content": prompt}]
                })
            )
            
            result = json.loads(response['body'].read())
            synthesized_text = result['content'][0]['text']
            
            # 참조 문서 생성 (명시적 메타데이터 추출)
            references = []
            for i, doc in enumerate(reranked_docs[:3]):
                # 메타데이터에서 직접 이미지 URI 추출
                metadata = doc.get('metadata', {})
                image_uri = (
                    doc.get('image_uri', '') or 
                    metadata.get('x-amz-bedrock-kb-byte-content-source', '') or
                    metadata.get('imageUri', '')
                )
                
                references.append({
                    "id": f"ref_{i+1}",
                    "content": doc['content'][:500] + "..." if len(doc['content']) > 500 else doc['content'],
                    "source": doc['source'] or "Neptune GraphRAG",
                    "score": doc.get('rerank_score', doc['score']),
                    # 명시적 필드 매핑
                    "source_file": doc.get('source_file', doc['source']),
                    "page_number": doc.get('page_number', 1),
                    "ocr_text": doc.get('ocr_text', doc['content']),
                    "image_uri": image_uri,
                    "has_multimodal": doc.get('has_multimodal', False),
                    "data_source_id": doc.get('data_source_id', ''),
                    "metadata": metadata
                })
            
            return {
                "text": synthesized_text,
                "references": references
            }
            
        except Exception as e:
            return {
                "text": f"응답 생성 중 오류: {str(e)}",
                "references": []
            }
    
    def _cohere_rerank(self, query: str, documents: list) -> list:
        """Cohere Reranking으로 문서 품질 보장"""
        try:
            if len(documents) <= 3:
                return documents  # 문서가 적으면 Reranking 생략
            
            # Cohere Rerank 호출 (최대 5개로 제한)
            docs_for_rerank = [{"text": doc["content"]} for doc in documents[:5]]  # 최대 5개
            
            response = self.bedrock_runtime.invoke_model(
                modelId='cohere.rerank-v3-5:0',
                body=json.dumps({
                    "query": query,
                    "documents": docs_for_rerank,
                    "top_k": min(5, len(docs_for_rerank)),
                    "return_documents": True
                })
            )
            
            result = json.loads(response['body'].read())
            reranked_results = []
            
            for item in result.get('results', []):
                # 원본 문서의 모든 메타데이터 보존
                import copy
                original_doc = copy.deepcopy(documents[item['index']])
                original_doc['rerank_score'] = item['relevance_score']
                reranked_results.append(original_doc)
            
            return reranked_results
            
        except Exception as e:
            # Reranking 실패시 원본 반환 (상위 5개)
            return documents[:5]
    
    def _get_ocr_from_dynamodb(self, document_id: str, page_number: str) -> str:
        """다이나모DB에서 OCR 텍스트 조회"""
        try:
            table = self.dynamodb.Table(self.ocr_table_name)
            response = table.get_item(
                Key={
                    'document_id': document_id,
                    'page_number': page_number
                }
            )
            
            if 'Item' in response:
                return response['Item'].get('ocr_text', '')
            return ''
            
        except Exception as e:
            return ''
    
    def _get_image_url_from_dynamodb(self, document_id: str, page_number: str) -> str:
        """DynamoDB에서 정확한 이미지 URL 조회"""
        try:
            table = self.dynamodb.Table(self.ocr_table_name)
            response = table.get_item(
                Key={
                    'document_id': document_id,
                    'page_number': page_number
                }
            )
            
            if 'Item' in response:
                return response['Item'].get('page_image_url', '')
            return ''
            
        except Exception as e:
            return ''
    
    def _extract_document_id_from_source(self, source_uri: str) -> str:
        """소스 URI에서 문서 ID 추출"""
        if not source_uri:
            return 'default_document'
        
        filename = source_uri.split('/')[-1].replace('.pdf', '').replace('.PDF', '')
        
        # 파일명에서 문서 ID 매핑
        if 'SOLAS' in filename:
            return 'solas_chapter2'
        elif 'DNV-RU-SHIP-Pt4' in filename:
            return 'dnv_pt4_ch6'
        elif 'DNV-RU-SHIP-Pt6' in filename:
            return 'dnv_pt6_ch5'
        elif 'FSS' in filename:
            return 'fss_code'
        elif 'IGC' in filename:
            return 'igc_code'
        elif 'Design guidance_Spoolcutting' in filename:
            return 'design_guidance_spoolcutting'
        elif 'Design guidance_Support' in filename:
            return 'design_guidance_support'
        elif 'Design_guidance_hull_penetration' in filename:
            return 'design_guidance_hull_penetration'
        elif 'Piping practice_Support' in filename:
            return 'piping_practice_support'
        elif 'Piping_practice_hull_penetration' in filename:
            return 'piping_practice_hull_penetration'
        else:
            return filename.lower().replace(' ', '_').replace('-', '_')