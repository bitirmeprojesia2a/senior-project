#!/bin/bash
# =================================================================
# Follow-up Mekanizması E2E Test Script
# =================================================================
# Kullanım: bash test_followup_e2e.sh [BASE_URL]
# Varsayılan: http://localhost:8000
#
# Her test grubu aynı context_id ile ardışık istekler gönderir.
# Her yanıtı inceleyerek follow-up davranışını doğrulayın.
# =================================================================

BASE_URL="${1:-http://localhost:8000}"
ENDPOINT="${BASE_URL}/query"

# Renkli çıktı
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

send_query() {
    local context_id="$1"
    local query="$2"
    local group="$3"
    local turn="$4"
    local expected="$5"

    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}[${group} - Tur ${turn}]${NC} ${YELLOW}${query}${NC}"
    echo -e "${GREEN}Beklenen:${NC} ${expected}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

    response=$(curl -s -X POST "${ENDPOINT}" \
        -H "Content-Type: application/json" \
        -d "{
            \"query\": \"${query}\",
            \"context_id\": \"${context_id}\",
            \"full_name\": \"Test Kullanici\",
            \"student_number\": \"21060731\",
            \"student_department\": \"Bilgisayar Muhendisligi\",
            \"student_faculty\": \"Muhendislik Fakultesi\"
        }" 2>/dev/null)

    # Yanıtı formatla
    if command -v python3 &> /dev/null; then
        echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
    elif command -v python &> /dev/null; then
        echo "$response" | python -m json.tool 2>/dev/null || echo "$response"
    else
        echo "$response"
    fi

    echo ""
    # Turlar arasında LLM/DB'nin işlemesine izin ver
    sleep 3
}

# =================================================================
echo -e "\n${GREEN}╔══════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  GRUP A: Temel Follow-up Algılama                ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════╝${NC}"
# =================================================================

send_query "test-A-$(date +%s)" \
    "CAP basvurusu nasil yapilir?" \
    "A" "1" \
    "is_follow_up=false, topic=CAP, dept=student_affairs+academic_programs"

# Aynı context_id'yi yeniden kullanmak için kaydet
CTX_A="test-A-followup-$$"

send_query "$CTX_A" \
    "CAP basvurusu nasil yapilir?" \
    "A" "1" \
    "is_follow_up=false, topic=CAP"

send_query "$CTX_A" \
    "Peki not ortalamasi kac olmali?" \
    "A" "2" \
    "is_follow_up=true, effective_query ~= CAP basvurusu icin not ortalamasi kac olmali?"

send_query "$CTX_A" \
    "Bunun icin hangi belge gerekli?" \
    "A" "3" \
    "is_follow_up=true, bunun zamiri cozulmeli"

send_query "$CTX_A" \
    "Erasmus basvurusu nasil yapilir?" \
    "A" "4" \
    "is_follow_up=false, yeni konu, topic degismeli"

# =================================================================
echo -e "\n${GREEN}╔══════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  GRUP B: Suffix/Marker Bug Fix Doğrulama          ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════╝${NC}"
# =================================================================

CTX_B="test-B-followup-$$"

send_query "$CTX_B" \
    "Kayit dondurma islemi nasil yapilir?" \
    "B" "1" \
    "is_follow_up=false, topic=Kayit Dondurma"

send_query "$CTX_B" \
    "Ucreti nedir?" \
    "B" "2" \
    "is_follow_up=true, nedir marker ile yakalanmali, cevap kayit dondurma ucreti hakkinda olmali"

send_query "$CTX_B" \
    "Ne zaman yapilir?" \
    "B" "3" \
    "is_follow_up=true, ne zaman marker ile yakalanmali"

send_query "$CTX_B" \
    "Kosullari nelerdir?" \
    "B" "4" \
    "is_follow_up=true, nelerdir marker ile yakalanmali"

# =================================================================
echo -e "\n${GREEN}╔══════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  GRUP C: Kısa / Anlamsız Soru Filtresi            ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════╝${NC}"
# =================================================================

CTX_C="test-C-followup-$$"

send_query "$CTX_C" \
    "Yaz okulu hakkinda bilgi verir misin?" \
    "C" "1" \
    "Normal soru, is_follow_up=false"

send_query "$CTX_C" \
    "Evet" \
    "C" "2" \
    "Turbo kelime, is_follow_up=false, bagimsiz degerlendirilmeli"

send_query "$CTX_C" \
    "Tesekkurler" \
    "C" "3" \
    "Turbo kelime, is_follow_up=false"

# =================================================================
echo -e "\n${GREEN}╔══════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  GRUP D: Konu Değişimi                            ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════╝${NC}"
# =================================================================

CTX_D="test-D-followup-$$"

send_query "$CTX_D" \
    "Harc ucreti ne kadar?" \
    "D" "1" \
    "topic=Harc ve Ogrenim Ucretleri, dept=finance"

send_query "$CTX_D" \
    "Taksitle odeyebilir miyim?" \
    "D" "2" \
    "is_follow_up=true, ayni konu, dept=finance"

send_query "$CTX_D" \
    "Burs basvurusu ne zaman?" \
    "D" "3" \
    "is_follow_up=false (baska konu), topic=Burs ve Destekler"

send_query "$CTX_D" \
    "Peki GNO sarti var mi?" \
    "D" "4" \
    "is_follow_up=true, burs baglaminda GNO sarti sorulmali"

# =================================================================
echo -e "\n${GREEN}╔══════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  GRUP E: Çok Departmanlı Geçiş                    ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════╝${NC}"
# =================================================================

CTX_E="test-E-followup-$$"

send_query "$CTX_E" \
    "Kayit dondurma nasil yapilir?" \
    "E" "1" \
    "dept=student_affairs"

send_query "$CTX_E" \
    "Bu durumda harc odenir mi?" \
    "E" "2" \
    "is_follow_up=true, kayit dondurma durumunda harc odenir mi"

send_query "$CTX_E" \
    "Peki ne kadar odenir?" \
    "E" "3" \
    "is_follow_up=true, dept=finance'a da gitmeli"

# =================================================================
echo -e "\n${GREEN}╔══════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  GRUP F: Belirsiz Zamir Çözümleme                 ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════╝${NC}"
# =================================================================

CTX_F="test-F-followup-$$"

send_query "$CTX_F" \
    "Staj basvurusu icin hangi belgeler gerekli?" \
    "F" "1" \
    "dept=student_affairs"

send_query "$CTX_F" \
    "Onlari nereden alirim?" \
    "F" "2" \
    "is_follow_up=true, onlari -> staj belgeleri"

send_query "$CTX_F" \
    "Suresi ne kadar?" \
    "F" "3" \
    "is_follow_up=true, suresi -> staj suresi"

# =================================================================
echo -e "\n${GREEN}╔══════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  GRUP G: LLM Rewrite Doğrulama                    ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════╝${NC}"
# =================================================================

CTX_G="test-G-followup-$$"

send_query "$CTX_G" \
    "Yatay gecis basvurusu nasil yapilir?" \
    "G" "1" \
    "Normal soru"

send_query "$CTX_G" \
    "Not ortalamasi kac olmali?" \
    "G" "2" \
    "LLM rewrite: Yatay gecis icin not ortalamasi kac olmali? (konuyu degistirmemeli)"

send_query "$CTX_G" \
    "Peki kontenjan var mi?" \
    "G" "3" \
    "LLM rewrite: Yatay gecis icin kontenjan var mi?"

# =================================================================
echo -e "\n${GREEN}╔══════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  GRUP I: Uçtan Uca Cevap Kalitesi                 ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════╝${NC}"
# =================================================================

CTX_I="test-I-followup-$$"

send_query "$CTX_I" \
    "Ikamet izni basvurusu nasil yapilir?" \
    "I" "1" \
    "dept=academic_programs, ikamet izni ile ilgili anlamli cevap"

send_query "$CTX_I" \
    "Peki ucreti ne kadar?" \
    "I" "2" \
    "is_follow_up=true, cevap IKAMET IZNI ucreti hakkinda olmali"

send_query "$CTX_I" \
    "Hangi belgeler gerekli?" \
    "I" "3" \
    "is_follow_up=true, cevap IKAMET IZNI belgeleri hakkinda olmali (genel belge listesi DEGIL)"

# =================================================================
echo -e "\n${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  TÜM TESTLER TAMAMLANDI                                  ║${NC}"
echo -e "${GREEN}║  Yanıtları inceleyerek follow-up davranışını doğrulayın   ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
