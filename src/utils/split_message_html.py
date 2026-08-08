import html
import re

def markdown_to_html(text: str) -> str:
    # 1. Escape karakter HTML mentah (<, >, &) terlebih dahulu
    escaped_text = html.escape(text)

    # 2. Konversi Code Block ```code```
    escaped_text = re.sub(
        r'```(?:[\w-]+)?\n?(.*?)```',
        r'<pre>\1</pre>',
        escaped_text,
        flags=re.DOTALL
    )

    # 3. Konversi Inline Code `code`
    escaped_text = re.sub(r'`([^`]+)`', r'<code>\1</code>', escaped_text)

    # 4. Konversi Heading (# Header)
    escaped_text = re.sub(r'^#+\s+(.*?)$', r'<b>\1</b>', escaped_text, flags=re.MULTILINE)

    # 5. Konversi Bold (**text**)
    escaped_text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', escaped_text)

    # 6. Konversi Italic (_text_) - Gunakan underscore agar tidak bentrok dengan '*' bullet list
    escaped_text = re.sub(r'(?<!\w)_(.*?)_(?!\w)', r'<i>\1</i>', escaped_text)

    return escaped_text


def split_message_html(text: str, max_length: int = 3500) -> list[str]:
    html_text = markdown_to_html(text)

    lines = html_text.split("\n")
    chunks = []
    current_chunk = ""

    # Tag Telegram yang valid
    tag_pattern = re.compile(r'</?(?:b|i|code|pre)>')

    for line in lines:
        if len(current_chunk + line + "\n") > max_length:
            temp_chunk = current_chunk.rstrip("\n")

            # Pelacakan tag terbuka dengan LIFO Stack
            open_tags = []
            for match in tag_pattern.finditer(temp_chunk):
                tag = match.group()
                if not tag.startswith("</"):
                    open_tags.append(tag[1:-1])
                else:
                    tag_name = tag[2:-1]
                    if open_tags and open_tags[-1] == tag_name:
                        open_tags.pop()

            # Tutup tag dengan urutan LIFO terbalik
            closing_tags = "".join(f"</{t}>" for t in reversed(open_tags))
            opening_tags = "".join(f"<{t}>" for t in open_tags)

            chunks.append(temp_chunk + closing_tags)
            current_chunk = opening_tags + line + "\n"
        else:
            current_chunk += line + "\n"

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks