# Announcement / Event A2A Karar Notu

Bu not, 2026-04-21 tarihinde netlestirilen yeni mimari hedefi kayda gecer:
`announcement` ve `event` akislari artik sadece local helper flow degil,
**ayri capability agent / ayri servis** olarak konumlandirilacaktir.

## Karar Ozeti

Eski karar:

- `announcement/event` kisa vadede ayri HTTP A2A servise alinmayacakti.

Guncel karar:

- `announcement` ayri capability agent/service olacak.
- `event` ayri capability agent/service olacak.
- Bunlar departman degil, **capability agent** siniridir.
- Department-level A2A devam ederken buna ek olarak capability-level A2A da desteklenecektir.

## Neden Bu Yola Gecildi

Kullanici hedefi net:

- her gerekli is parcasi mantikli ve temiz bicimde ayri agent olsun,
- dagitik mimari sadece departmanlarla sinirli kalmasin,
- ana orkestrator butun bu servisleri koordine etsin.

Bu hedefe gore:

- `student_affairs`, `academic_programs`, `finance` = department orchestrator servisleri
- `announcement`, `event` = capability agent servisleri

Yani `announcement/event` ayrimi "mantiksiz" degil; tam tersine,
mevcut ozel akislar zaten agent/service siniri olmaya uygundur.

## Guncel Hedef Topoloji

- `main_orchestrator`
- `student_affairs_orchestrator service`
- `academic_programs_orchestrator service`
- `finance_orchestrator service`
- `announcement capability service`
- `event capability service`

Burada:

- department servisleri kendi ic uzman ajanlarini yonetir,
- capability servisleri tek bir ozel yetenegi tasir,
- ana orkestrator hem department hem capability dispatch yapabilir.

## 2026-04-21 Uygulanan Ilk Adim

Bu karar artik sadece dokuman seviyesinde degil, kod seviyesinde de baslatildi:

- `event` ilk kez gercek bir `EventAgent` sinirina tasindi.
- `announcement` ve `event` icin capability HTTP transport eklendi.
- `agent_service` artik sadece departman degil,
  `announcement` ve `event` target'larini da ayaga kaldirabiliyor.
- Registry/health/build metadata capability agent'lari da kaydedebiliyor.
- Docker rollout tarafina capability servis overlay'i eklendi.
- Canli Docker smoke'ta announcement ve event servisleri ayri container olarak ayağa kaldirildi;
  public API sorgulari `departments_involved=["announcement"]` ve
  `departments_involved=["event"]` ile dondu.
- Container loglari capability servislerine gercek `POST /a2a/dispatch 200 OK`
  geldiginin kanitini verdi; yani bu gecis yalnizca kod seviyesinde degil,
  canli A2A akisinda da dogrulandi.

Yani bu is "sonra dusunuruz" backlog'u olmaktan cikti;
gercek gecis basladi.

## Uygulama Prensibi

Bu gecis yine de su sekilde ilerlemeli:

1. Orkestrasyon ve servis siniri genellestirilsin.
2. Announcement/event capability agent'lari stabil hale gelsin.
3. Sonra gerekirse daha ince taneli uzman ajanlar da ayri servislesebilsin.

Yani hedef "hemen tum uzmanlari patlatip mikroservis yapmak" degil;
ama **gerekli ve mantikli her agent'i dagitik sinira tasimak** artik resmi hedeftir.
