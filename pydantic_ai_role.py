from enum import Enum
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from openai import AsyncOpenAI
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic import BaseModel, Field

# Inisialisasi klien OpenAI
client = AsyncOpenAI(
    base_url="http://localhost:4000",
    api_key="sk-1234" # Ganti dengan API key yang valid jika diperlukan oleh server lokal Anda
)

class JobCategoryAi(Enum):
    BACKEND = "backend"
    FRONTEND = "frontend"
    FULLSTACK = "fullstack"
    NONE = "none"

class RoleJob(BaseModel):
    job_category: JobCategoryAi = Field(..., alias="JobCategory")
    reason: str

# Inisialisasi model OpenAI
model = OpenAIModel(
    'gpt-4o-mini', # Atau model lain yang tersedia di server lokal Anda
    provider=OpenAIProvider(openai_client=client)
)

async def _generate_role_internal(role: str, vacancy: str, min_salary: int) -> RoleJob:
    """Fungsi async internal untuk generasi peran (sekarang tidak banyak berubah dari sebelumnya,
       karena ini sudah async)"""
    agent = Agent(
        model,
        output_type=RoleJob,
        instructions="""
        Anda adalah asisten kategorisasi pekerjaan. Berdasarkan peran, deskripsi lowongan, dan gaji minimum, klasifikasikan pekerjaan tersebut.

        Pilih FRONTEND jika:
        - Judul atau deskripsi menyebutkan teknologi frontend seperti React js, Next js, Vue.js, Angular, HTML, CSS, JavaScript untuk pengembangan UI.
        - Tanggung jawab utama adalah mengerjakan antarmuka pengguna dan pengalaman pengguna.
        - Secara eksplisit menyatakan "Frontend Developer".

        Pilih BACKEND jika:
        - Judul atau deskripsi menyebutkan teknologi backend seperti Golang, Python (untuk backend misal Django, Flask), Node.js (untuk backend), Java (untuk backend, kecuali instruksi untuk NONE), Ruby, C#, dll.
        - Tanggung jawab utama adalah logika sisi server, database, API, skrip, atau otomatisasi.
        - Secara eksplisit menyatakan "Backend Developer".

        Pilih FULLSTACK jika:
        - Judul atau deskripsi secara eksplisit menyatakan "Fullstack Developer" atau mengindikasikan tanggung jawab yang mencakup tugas frontend dan backend.
        - Peran tersebut membutuhkan kemahiran dalam teknologi frontend dan backend.

        Pilih NONE jika SALAH SATU kondisi berikut terpenuhi:
        - Pekerjaan di luar bidang pengembangan perangkat lunak TI (misalnya, dokter, guru, pemasaran, penjualan).
        - Pekerjaan tersebut utamanya membutuhkan bahasa tingkat rendah seperti C, C++, Rust, kecuali jika jelas untuk komponen backend aplikasi tingkat tinggi.
        - Pekerjaan tersebut membutuhkan bahasa PHP atau Java (Baik Frontend atau Backend jika menjadikan ini syarat utama maka masukkan none kecuali jika hanya mengetahui atau understand maka tidak termasuk none).
        - Gaji minimum yang diberikan di bawah 4.000.000 (empat juta), KECUALI jika gaji minimum ditulis 0 ataupun tidak dicantumkan ataupun gajinya tidak jelas (yang berarti gaji tidak menjadi filter atau dapat dinegosiasikan).
        - Pekerjaan tersebut membutuhkan pengalaman *lebih dari* 3 tahun. Jika membutuhkan 3 tahun atau kurang, atau jika pengalaman tidak disebutkan, kondisi spesifik untuk 'NONE' ini tidak berlaku.
        - Judul atau deskripsi terlalu kabur untuk menentukan kategori pengembangan perangkat lunak TI yang jelas.

        Berikan alasan singkat untuk klasifikasi Anda.
        """
    )
    prompt_text = f"Tentukan kategori pekerjaan untuk peran: '{role}' dengan deskripsi lowongan: '{vacancy}'. Gaji minimum yang ditawarkan adalah {min_salary}."
    # print(f"DEBUG: Mengirim prompt ke LLM: {prompt_text}")
    result = await agent.run(prompt_text)
    return result.output

# generate_role sekarang adalah fungsi async
async def generate_role(role: str, vacancy: str, min_salary: int) -> RoleJob:
    """
    Secara asinkron menentukan kategori pekerjaan dari peran, deskripsi lowongan, dan gaji minimum.

    Args:
        role: Judul peran pekerjaan
        vacancy: Deskripsi lowongan
        min_salary: Gaji minimum yang ditawarkan. Gunakan 0 jika tidak ditentukan atau dapat dinegosiasikan.

    Returns:
        Objek RoleJob dengan kategori dan alasan.
    """
    try:
        # Langsung menggunakan await untuk memanggil fungsi async internal
        result = await _generate_role_internal(role, vacancy, min_salary)
        return result
    except Exception as e:
        print(f"Error saat generate role: {e}")
        # Mengembalikan nilai default jika terjadi error
        raise ValueError("Gagal menghasilkan kategori pekerjaan") from e
