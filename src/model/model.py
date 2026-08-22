
import os 
from dotenv import load_dotenv
from google import genai
from google.genai import types
load_dotenv()


client = genai.Client(api_key=os.getenv("GENAI_API_KEY"))

async def interaction_ai(prompt: list[str]) -> str:
    interaction = await client.aio.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
        config={
            "system_instruction": "Kamu adalah seorang dosen jurusan teknik informatika yang menjawab pertanyaan mahasiswa dengan bahasa yang santai dan mudah dimengerti. Jawaban harus relevan dengan pertanyaan dan tidak boleh keluar dari konteks jurusan teknik informatika. Jawaban harus jelas, ringkas, dan mudah dipahami. kamu tidak boleh menjawab pertanyaan di luar konteks jurusan teknik informatika, jawablah dengan bahasa Indonesia yang baik dan benar.",
        }
    )
    return interaction.text

async def embed_ai(contents:types.ContentListUnion | types.ContentListUnionDict, taskType:str) ->types.EmbedContentResponse:
    embed = await client.aio.models.embed_content(
        model="gemini-embedding-2",
        contents=contents,
        config=types.EmbedContentConfig(task_type=taskType)
    )
    return embed