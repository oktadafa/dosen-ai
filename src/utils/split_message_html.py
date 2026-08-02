import re


def split_message_html(text: str, max_length: int = 3500) -> list[str]:
    html_text = re.sub(r"^#+\s+(.*?)$", r"<b>\1</b>", text, flags=re.MULTILINE)
    html_text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", html_text)
    html_text = re.sub(r"\*(.*?)\*", r"<i>\1</i>", html_text)
    html_text = re.sub(r"`(.*?)`", r"<code>\1</code>", html_text)

    lines = html_text.split("\n")
    chunks = []
    current_chunk = ""

    tags = [
        {"open": "<b>", "close": "</b>"},
        {"open": "<i>", "close": "</i>"},
        {"open": "<code>", "close": "</code>"},
    ]

    for line in lines:
        if len(currentChunk_test := current_chunk + line) > max_length:
            temp_chunk = current_chunk.strip()
            tags_to_close = []

            for tag in tags:
                open_count = len(re.findall(re.escape(tag["open"]), temp_chunk))
                close_count = len(re.findall(re.escape(tag["close"]), temp_chunk))
                
                if open_count > close_count:
                    temp_chunk += tag["close"]
                    tags_to_close.insert(0, tag["open"])

            chunks.append(temp_chunk)
            current_chunk = "".join(tags_to_close) + line + "\n"
        else:
            current_chunk += line + "\n"
    if current_chunk.strip() != "":
        chunks.append(current_chunk.strip())

    return chunks