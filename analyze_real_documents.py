#!/usr/bin/env python3
"""
실제 Neptune KB 문서 내용 분석
"""
import sys
sys.path.append('/home/ec2-user/workshops/shi-graphrag-chatbot')

def analyze_real_documents():
    print("🔍 실제 Neptune KB 문서 내용 분석...")
    
    try:
        from agents.plan_execute_agent.agent import PlanExecuteAgent
        
        agent = PlanExecuteAgent()
        
        # 다양한 키워드로 검색해서 실제 문서 파악
        test_queries = [
            "safety", "fire", "design", "piping", "hull", 
            "DNV", "SOLAS", "FSS", "support", "penetration"
        ]
        
        all_sources = set()
        document_samples = {}
        
        for query in test_queries:
            print(f"\n📝 '{query}' 검색 중...")
            results = agent._execute_neptune_search(query)
            
            for result in results:
                source = result.get('source', 'Unknown')
                content = result.get('content', '')
                
                if source and source != 'Unknown':
                    all_sources.add(source)
                    
                    # 각 소스별 샘플 내용 저장
                    if source not in document_samples:
                        document_samples[source] = content[:200] + "..."
        
        print(f"\n📚 실제 검색되는 문서 소스 ({len(all_sources)}개):")
        for i, source in enumerate(sorted(all_sources), 1):
            print(f"  {i}. {source}")
            if source in document_samples:
                print(f"     내용: {document_samples[source]}")
        
        # S3 파일명과 비교
        print(f"\n🔄 S3 파일명과 검색 소스 비교:")
        s3_files = [
            "DNV-RU-SHIP-Pt4 Ch6.pdf",
            "DNV-RU-SHIP-Pt6 Ch5 Sec4.pdf", 
            "Design guidance_Spoolcutting.PDF",
            "Design guidance_Support.PDF",
            "Design_guidance_hull_penetration.PDF",
            "SOLAS Chapter II-2_Construction Fire Protection, Fire Detection and Fire Extinction.pdf",
            "FSS.pdf",
            "IGC_Code_latest.pdf",
            "SOLAS_2017_Insulation_penetration.pdf",
            "Piping practice_Support.PDF",
            "Piping_practice_hull_penetration.PDF"
        ]
        
        print("S3 파일명:")
        for file in s3_files:
            print(f"  - {file}")
        
        print("\n실제 검색 소스:")
        for source in sorted(all_sources):
            print(f"  - {source}")
            
        return sorted(all_sources)
        
    except Exception as e:
        print(f"❌ 문서 분석 실패: {e}")
        return []

if __name__ == "__main__":
    sources = analyze_real_documents()