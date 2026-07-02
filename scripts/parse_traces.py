import glob
import re
import json

def parse_markdown_traces():
    conversations = []
    
    # Sort files C1.md to C10.md numerically
    paths = sorted(glob.glob('GenAI_SampleConversations/C*.md'), key=lambda x: int(re.search(r'C(\d+)\.md', x).group(1)))
    
    for path in paths:
        c_id = re.search(r'C(\d+)\.md', path).group(1)
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        turns = []
        # Split by turns
        turn_blocks = re.split(r'### Turn \d+', content)
        
        # The first block is the header, ignore it
        for idx, block in enumerate(turn_blocks[1:], start=1):
            block = block.strip()
            if not block:
                continue
                
            # Extract User message
            user_match = re.search(r'\*\*User\*\*\s*\n*\s*>\s*(.*?)\n', block, re.DOTALL)
            if not user_match:
                # Some blocks might have multi-line blockquotes
                user_match = re.search(r'\*\*User\*\*\s*\n*\s*>\s*(.*?)(?=\n\n\*\*Agent\*\*)', block, re.DOTALL)
                
            if not user_match:
                continue
                
            user_message = user_match.group(1).strip()
            # Clean > characters if multi-line
            user_message = "\n".join([line.lstrip('> ').strip() for line in user_message.split('\n')])
            
            # Extract Agent message block
            agent_part = block.split('**Agent**')[-1].strip()
            
            # Extract end_of_conversation
            eoc_match = re.search(r'_`end_of_conversation`:\s*\*\*?(true|false)\*\*?_', agent_part, re.IGNORECASE)
            end_of_conversation = eoc_match.group(1).lower() == 'true' if eoc_match else False
            
            # Extract recommendations (if any) from table
            expected_recs = []
            if 'URL' in agent_part:
                for line in agent_part.split('\n'):
                    if '|' in line and not 'Name' in line and not '---' in line:
                        parts = [p.strip() for p in line.split('|')]
                        if len(parts) >= 8:
                            name = parts[2]
                            url = parts[7]
                            # Clean markdown link syntax from URL if present
                            url_match = re.search(r'<(.*?)>', url)
                            if url_match:
                                url = url_match.group(1)
                            expected_recs.append(name)
            
            # Get agent reply (excluding the table and metadata)
            agent_lines = []
            for line in agent_part.split('\n'):
                line_stripped = line.strip()
                if line_stripped.startswith('|') or line_stripped.startswith('_') or not line_stripped:
                    continue
                agent_lines.append(line_stripped)
            agent_reply = " ".join(agent_lines)
            
            turns.append({
                "turn_index": idx,
                "user_message": user_message,
                "expected_agent_reply": agent_reply,
                "expected_recommendations": expected_recs,
                "expected_end_of_conversation": end_of_conversation
            })
            
        conversations.append({
            "conversation_id": f"C{c_id}",
            "turns": turns
        })
        
    with open('data/parsed_traces.json', 'w', encoding='utf-8') as f:
        json.dump(conversations, f, indent=2, ensure_ascii=False)
    print(f"Parsed {len(conversations)} conversations successfully.")

if __name__ == '__main__':
    parse_markdown_traces()
