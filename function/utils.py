import json
import re

def extract_mentioned_user(comment_text):
        """
        Extract mentioned username from comment text (e.g., @username)
        """
        # Look for @username pattern
        match = re.search(r'@(\w+)', comment_text)
        if match:
            return match.group(1)
        return None

def build_parent_chain(comment, id_to_comment, depth=0, max_depth=1):
    """
    Recursively build parent chain string for a comment, up to max_depth.
    """
    if depth >= max_depth:
        return ''
    parent_id = comment.get('parent_comment_id')
    if parent_id is not None and parent_id in id_to_comment:
        parent = id_to_comment[parent_id]
        parent_str = build_parent_chain(parent, id_to_comment, depth+1, max_depth)
        return f"\n    (In reply to: Author: {parent.get('author_name', 'Unknown')}, Body: {parent.get('body', 'No content')}{parent_str})\n\t"
    return ''

def formulate_tree(context, tree_id):
    nodes = context['graph']['nodes']
    tree_nodes = [n for n in nodes if n.get('tree_id', []).count(tree_id) > 0]
    if not tree_nodes:
        print(f"No nodes found for tree_id {tree_id}")
        return False

    # Gather all comments in the tree as context (author, body, parent_comment_id only)
    id_to_comment = {c.get('id'): c for c in context.get('comments', []) + context.get('new_added_comment', [])}
    tree_comments = []
    for n in tree_nodes:
        c = id_to_comment.get(n['id'])
        if c:
            parent_chain = build_parent_chain(c, id_to_comment)
            tree_comments.append(f"Author: {c.get('author_name', 'Unknown')}: {parent_chain} {c.get('body', 'No content')}")
    context_text = "\n".join(tree_comments)
    return context_text

def extract_json_from_markdown(markdown_text):
    # Remove leading and trailing triple backticks and optional "json"
    cleaned = re.sub(r'^```(?:json)?\s*', '', markdown_text.strip(), flags=re.IGNORECASE)
    cleaned = re.sub(r'```$', '', cleaned.strip())
    return cleaned.strip()

def list_tree_ids(context):
    tree_ids = set()
    nodes = context['graph']['nodes']
    for node in nodes:
        tids = node.get('tree_id', [])
        if isinstance(tids, int):
            tids = [tids]
        for tid in tids:
            if tid >= 0:
                tree_ids.add(tid)
    tree_ids = list(tree_ids)
    return tree_ids