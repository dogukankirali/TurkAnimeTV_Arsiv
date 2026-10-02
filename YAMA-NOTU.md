# Yama Notu — 02.10.2026

## 🎨 Bu güncelleme: TürkAnime'nin 2025-26 teması + aynı numaralı OVA bölümleri

**Kısa sürüm (paylaşmak için):**

> **🎨 Site artık kapanmadan önceki TürkAnime'nin son temasını kullanıyor.**
> turkanime.tv 19 Eylül'de kapanmadan önce koyu zeminli, `#b22222` kırmızı
> vurgulu, Arial yazı tipli son hâlini kullanıyordu. Bu tema birebir uygulandı;
> sağ üstteki güneş/ay simgesiyle **açık temaya** geçilebiliyor ve seçim
> tarayıcıda hatırlanıyor.
>
> **Bölüm listesindeki karışıklık giderildi.** Bazı animelerde OVA bölümleri ana
> serinin bölümleriyle **aynı numarayı** taşıyordu; listede yan yana iki tane «#3»
> görünüyor, hangisinin OVA olduğu anlaşılmıyordu. Artık OVA / Special / Final
> bölümleri numaranın yanındaki küçük bir rozetle ayrılıyor.
>
> **Telefondaki yatay kaydırma hatası kapatıldı.** Üst çubuk 390 px'lik bir
> telefonda 459 px'e taşıyordu (sayfa yana kayıyordu). Artık sığıyor.

### Ayrıntılar

**Tema — iskelet birebir (3. tur: gerçek 2026 kopyası + kart yapısı)**

- ⭐ **Ölçüm düzeltmesi.** 2. turda referans olarak
  `anasayfa_20260814102725.html` (73 KB) alınmıştı. Arşivde aynı sitenin
  **`anasayfa_20260619135216.html` (108 KB)** kopyası var ve onda çok daha
  fazla bileşen bulunuyor (sınıf sayımı): `.panel` 23→17, `.panel-ust` 12→7,
  `.panel-title` 18→13, **`.list-group-item` 20→0**, `.thumbnail` 21→10,
  `.media-heading` 20→10. Yani 08-14 kopyası eksik/lazy kalmış; gerçek tasarım
  06-19'da.
- Eksik bileşenler tamamlandı:
  - **Slayt şeridi** — `.col-xs-12.top-airing-container > .swiper-container
    .top-airing-slider > .swiper-wrapper > .swiper-slide > a.top-airing-item >
    img + .top-airing-overlay > span.top-airing-title` + `.top-airing-prev`
    /`.top-airing-next`. Swiper JS yüklenmiyor; CSS zaten turkanime'den geliyor,
    yalnız Swiper'ın çalışma anında yazdığı slayt ölçüsü (111 px) ve kaydırma
    taklit edildi. Kapaklar AniList'ten (kapağı olmayan seri şeride girmiyor).
  - **Turkanime'in gerçek kartı** — `.col-md-6.col-sm-6.col-xs-12 >
    .panel.panel-visible > .panel-ust-ic > .panel-title > a.baloon` +
    `.panel-body > a.thumbnail.pull-left > img(90×128)` + `span.media-heading`
    + `.row > span.bold.media-object / i.fa-angle-right / i.fa-clock`.
    Kart, arama sonuçları/liste/öneri ızgarasının tamamında kullanılıyor.
    ⚠ Karttaki “Çeviri : &lt;fansub&gt;” ve “yaklaşık X saat önce eklendi”
    satırları bölüm/fansub düzeyinde veri ister; bu arşivde link verisi bölüm
    düzeyinde tutulduğu için aynı satırlar bölüm ve kaynak bilgisiyle
    dolduruldu — uydurma fansub/tarih yazılmadı.
  - **Ana sayfa düzeni** — `.col-xs-8` içinde `.col-xs-6 + .col-xs-6`
    (GÜNÜN ÖNERİSİ / ARŞİV DURUMU) ve altında `#orta-sekme` sekmeli panel;
    `.col-xs-4` yan kolonda `.list-group` (arşiv durumu) + `#aktif-sekme`
    (Harfler / Türüne Göre) + `.menum` (en çok kaynaklı seriler).
  - **Navbar** — gerçek 2026 kabuğundaki `li.dropdown.basvuru-menu` ile aynı
    yerde/yapıda `li.dropdown.arsiv-menu` (`ARŞİV ▾` → Kullanım, Yama notu,
    Hakkında, GitHub).
- **Kapatılan iki ölçülmüş hata:**
  - `.btn{height:var(--btn-h)}` kuralı TÜM `.btn`'leri 40 px yapıyordu;
    turkanime'in harf çubuğu `.btn.btn-default` (bootstrap: 30 px) bu yüzden
    uzundu (`.panel-ust` 51 px'e karşı referansta 41 px).
  - `.menum` satırlarında etiketler `<li>`nin doğrudan çocuğuydu ve sağdaki
    sayı panelin dışına taşıyordu; turkanime'de yapı
    `<li><a class="baloon">…<span class="label pull-right">`.
  - Ayrıca `#app` bir `.col-xs-12` olduğu için tüm görünüm 30 px içeride ve
    kolonlar 65 px dar kalıyordu; `#app` artık `class="row"` (turkanime'de
    `#arkaplan > .row > .col-xs-8`).
- **Doğrulama:** aynı öğelerde site ↔ referans ölçümü (`tasarim-diff.py`);
  renk/font/kenarlık/köşe değerleri birebir, genişlik farkı ≤5 px (kaydırma
  çubuğu), yatay taşma 0 (1280 ve 390 px), konsol hatası yok. Slayt ileri/geri,
  sekme geçişi, harf çubuğu, bölüm filtresi, tema anahtarı ve `ARŞİV` menüsü
  tarayıcıda sınandı.

**Tema — iskelet birebir (2. tur)**

- İlk turda yalnız **renk katmanı** taşınmıştı (tokenlar doğruydu ama sayfa
  iskeleti bu sitenin kendi düzeniydi). Kullanıcı geri bildirimi üzerine
  **gerçek DOM iskeleti** taşındı.
- Artık TürkAnime'nin **kendi CSS yığını** yükleniyor (`assets/css/`):
  `bootstrap.min.css` (3.3.7) · `bootstrap.css` (turkanime özel, v3.3.0.19) ·
  `style.css` (v3.3.0.23, açık tema) · `dark.css` (v3.3.0.23, koyu tema,
  varsayılan) · `mobil.css`. Kaynak: arşivdeki 2025-26 anlık görüntüsünden
  çözülen dosyaların aynısı. CSS'in istediği görseller de geldi
  (`assets/imajlar/`, 16 dosya).
- Kabuk, arşivdeki gerçek sayfadan **birebir**:
  `<header class="navbar navbar-inverse navbar-fixed-top"><article class="container">`
  + `ul.nav.navbar-left` / `ul.nav.navbar-right#search` + `.toggleDark`,
  ardından `<article class="container"><div id="arkaplan">` + logo satırı +
  `div.navbar.navbar-inverse.panel > .panel-ust > .btn-group.alphabet`
  (A→Z çubuğu) ve `footer.clearfix > .Altkisim > .container`.
- Görünümler de aynı dile taşındı: `.panel > .panel-ust > .panel-title`,
  `.panel-menu > ul.panel-tabs.nav-justified`, `#orta-icerik` /
  `#aktif-icerik`, `#filtre-input-bolum`, `.list-group-item` bölüm satırları,
  `.menum` sıralı listeler, `.col-xs-8` / `.col-xs-4` kolonları.
- Ölçüm (yerel render, 1280px, referans = arşivden render edilmiş gerçek sayfa):
  `body` `rgb(46,48,57)` · `#arkaplan` `rgb(30,32,38)` · `.panel-ust`
  `rgb(23,25,31)` · `.Altkisim` `rgb(34,36,43)` · harf çubuğu genişliği `918px`
  · `.container` `1024px` — **referansla birebir aynı**. Yatay taşma 0 (1280 ve
  390 px). Açık tema `#d7d7d7` / `#fff` (TürkAnime'nin açık teması).
- Davranış korunuyor: sekme geçişi, harf çubuğu (368 seri), `#filtre-input-bolum`
  (100 → 10 satır), tema anahtarı ve `localStorage` kalıcılığı, tüm rotalar.

**Tema renkleri**

- Kaynak: Wayback anlık görüntüsü `20260814102725` → `style.css?v=3.3.0.23` +
  `dark.css?v=3.3.0.23`. TürkAnime'nin 2025-26 canlı teması varsayılan olarak
  koyuydu (`<body id="bd" class="dark">`, `theme-color:#222222`).
- `:root` tokenları TürkAnime paletine çevrildi: zemin `#2e3039`, içerik
  `#1e2026`, panel `#1D1F25`, üst çubuk `#23252C`, kenarlık `#22242b`,
  metin `#c5c8ce`, vurgu **`#b22222`**.
- İçerik genişliği 1180 → **1024 px** (TürkAnime `.container`).
- Google Fonts kaldırıldı (Bricolage Grotesque + Figtree) → TürkAnime'nin kendi
  `"Arial",Tahoma,Verdana,Helvetica,sans-serif` yığını; `font-size:1.1em`,
  `line-height:1.475`, `font-weight:lighter`.
- Açık tema `body.light` ile (`#d7d7d7` zemin, `#fff` içerik, `#eee` kartlar);
  üst çubuk ve altbilgi TürkAnime'de olduğu gibi iki temada da koyu kalır.
  Seçim `localStorage` anahtarı `ta-tema`.

**Bölüm numarası çakışması**

- Ölçüm: **65 dosya · 180 numara grubu · 365 kayıt** aynı `no`yu paylaşıyor.
  Kaynak DB'de OVA/Special/Final bölümleri ana seriye 1'den yeniden numaralanmış.
- Bağlantı adresi zaten `bolumIdFor` ile slug'a düşüyordu (davranış aynı kaldı);
  yalnızca listede ayırt edici bir rozet eklendi. Rozet, grubun tamamı aynı
  niteliği taşıyorsa gösterilmez (bilgi vermez).

**Veri düzeltmeleri**

| Dosya | Önce | Sonra |
|---|---|---|
| `b/one-piece-movie-6-omatsuri-danshaku-to-himitsu-no-shima.js` | 2 kayıt (ikincisinde 0 link) | 1 kayıt (4 link) |
| `b/suki-na-mono-wa-suki-dakara-shou-ga-nai.js` 2. bölüm | player `VK`, URL `myvi.tv` | player `MYVI` |
| INDEX bölüm sayısı | 71.689 | 71.688 |
| INDEX ↔ `b/` uyuşmazlığı | 0 | 0 |
| Link sayısı | 317.067 | 317.067 (değişmedi) |

**Diğer**

- README'deki `<!-- TODO: Ekran görüntüsü eklenecek -->` maddesi kapandı;
  4 gerçek ekran görüntüsü `ekran-goruntuleri/` altında.
- Üst çubuktaki arama kutusuna `min-width:0` eklendi (mobil yatay taşma).

---

# Yama Notu — 28.09.2026

## 🔄 Önceki güncelleme: MOBİL (28.09.2026 gece)

**Kısa sürüm (paylaşmak için):**

> **📱 Site artık mobil için düzeltildi.** Ziyaretçilerin **%65,9'u telefondan**
> geliyordu ama site hiç telefonda denenmemişti. Bu çalışmada 11 düzeltme yapıldı.
>
> **En önemlisi — site artık çok daha hızlı açılıyor.** Sitenin kapak görselleri ve
> özetler için indirdiği 2,7 MB'lık dosya, sayfa görünür olmadan önce yükleniyordu.
> Artık arka planda geliyor; **sayfa çok daha çabuk açılıyor** ve veri tasarrufu oluyor.
>
> **Telefonda 1166 bölüm yavaş yükleniyordu.** One Piece gibi dizilerde bölüm
> listesinin tamamı tek seferde basılıyordu. Artık **200'er bölümlük sayfalar** hâlinde
> geliyor; 1166 düğüm yerine 200 düğüm yükleniyor.
>
> **"Bölüm bulunamadı" yerine ne olduğu yazıyor.** Eskiden bir uyarı kutusu
> ekranın ortasına çıkıyordu; küçük bir cihazda 24 saniyelik bir oturumu
> durduruyordu. Artık uyarı ekrana yazılıyor, kodu çalışmıyorsunuz.
>
> **"İndirildi" yalanı sona erdi.** Telefonda indirme sessizce başarısız olabiliyor
> ama "indirildi ✓" yazılıyordu. Artık gerçeği söylüyor: indirildi, panoya kopyalandı,
> ya da hiçbiri olmadı — hangisise o.
>
> **Geri düğmesi artık çalışıyor.** Telefonda "geri" tuşu 3 sayfa geri gitmek yerine
> ana sayfaya atıyordu. Artık bölüm listesi sayfaları ve sezon değişimleri geri
> tuşuyla doğru çalışıyor; adres çubuğundaki adres de doğruyu gösteriyor.
>
> **Dokunma hedefleri büyütüldü.** Küçük düğmeler 30–38 pikseldi (parmakla
> vurmak zor). Telefonda 40–44 piksele çıkarıldı; fareyle kullanan masaüstü
> kullanıcısı etkilenmiyor.
>
> **Kapak görselleri küçültüldü.** 460 piksel yerine gerektiği boyut indiriliyor;
> liste sayfasında görsel verisi yaklaşık **yarıya** indi.
>
> **Adres çubuğu hesaba katıldı** — çentikli telefonlarda oynatıcı ve bölüm listesi
> artık ekran dışına taşmıyor. Sistem ayarından "animasyonları azalt" seçili olanlar
> için de sayfa hareketi duruyor.
>
> **Artık oynatıcı sorunlarını ölçebiliyoruz.** Daha önce "oynatıcı bozuk mu, yoksa
> kullanıcı başka yere mi gidiyor" sorusunu **hiçbir veriyle cevaplayamıyorduk**.
> Artık her oynatıcı açılışı, engellenen kaynak, kaynak değiştirme ve "kaynak
> linkini aç" tıklaması sayılıyor. **1 hafta sonra bu soru ilk kez veriyle
> cevaplanabilecek.**
>
> **Küçük not:** Sistem "animasyonları azalt" açıksa sonsuz dönen yükleme
> animasyonu duruyor.

---

**Teknik özet (geliştirici için):**

| | |
|---|---|
| `search.html` | 722.663 → **755.580 B** |
| Değişen dosya | yalnız `search.html` (+669 / −50 satır) |
| Plandan uygulanan | 13 maddenin **11**'i |
| Tur içinde bulunan hata | **13** (kendim yazdıklarım) |
| Bağımsız denetim | 1 KRİTİK + 6 ORTA + 9 DÜŞÜK |
| Son tarama | 8/8 sayfa **0 JS hatası** |

**Doğrulama (ölçüm, tahmin değil):**

| | |
|---|---|
| Oynatıcı iframe isteği | `video.sibnet.ru/shell.php` **tam 1 kez** (ağ günlüğü) |
| Bölüm listesi DOM | 1 166 → **200** düğüm, 6 sayfa |
| Kapak görseli | `naturalWidth` 460 → **158 px**; 13 görselde 12 × `medium` |
| AniList zenginleştirme | puan **8,7** · 1999 · 5 tür · özet |
| Geri tuşu | sayfa 3 → 1 ✅ · sezon 6 → 1 ✅ · derin bağlantı `?s=2&p=3` ✅ |
| Telemetri | 4 olay ağ/günlük üzerinden doğrulandı |
| HTML yapısı | `kaynak_denetle.py` (yeni denetim eklendi) temiz |

**Uygulanmayan 2 madde — gerekçesiyle:**

- **Gerçek cihaz testi (360×800):** yapılamadı, viewport emülasyonu aracı yok.
  **Ölçülemediğini ölçülmüş gibi yazmadık.**
- **Service Worker:** bilinçli ertelendi. En yüksek kazanç *ve* en yüksek risk;
  bayat içerik sunma tehlikesi var, sıfır hata standardını riske atmak doğru değil.

Ayrıntı: `Raporlar/DUZELTME-11-MOBIL-QOL-UYGULAMA.md`

---

## 🧹 Önceki güncelleme: bağlantı temizliği (28.09.2026 sabah)

> **TürkAnime Arşiv güncellendi.**
>
> **Görsel:** Yeni logo eklendi. Artık her sayfada büyük ve net görünüyor.
>
> **Çalışmayan bağlantılar temizlendi.** 78 bağlantı (57 "Byse", 19 "Pixeldrain",
> 2 "VOE") tespit edildi, her biri tek tek doğrulanarak hem bu bölümlerden hem de
> arşiv veritabanından kaldırıldı. Artık o bölümlerde kırık oynatıcı yerine
> çalışan kaynaklar görünecek.
>
> **Önemli:** Daha önce "ölü" ilan edilen bir kısım bağlantılar aslında
> **çalışıyormuş**; ölçüm düzeltildi ve geri getirildi. Ölü ilan ettiğimiz
> bağlantıların çoğu sağlamdı.
>
> **Bazı VOE bağlantıları** reklam sayfasına yönlendiriyordu. Şimdilik
> dokunmadık — bazı kullanıcılarda gerçek oynatıcı çalışabiliyor.
>
> **Bölüm listesi düzeltildi.** Aynı numarayı taşıyan bölümler (mesela bir animede
> hem "3. Bölüm" hem "OVA 3. Bölüm") artık karışmıyor; tıkladığınızda doğru bölüm açılıyor.
>
> **Çok sezonlu animeler için sezon filtresi.** Bir animede 1'den fazla sezon varsa
> üstte "1. Sezon / 2. Sezon" düğmeleri çıkıyor; tıkladığınızda sadece o sezonun
> bölümleri listeleniyor.
>
> **Oynatıcı artık en iyi kaynağı seçiyor.** Daha önce Google Drive her zaman
> otomatik açılıyordu; artık güvenilir kaynak (Sibnet, Mail, UQload…) seçiliyor.
>
> **"Ana sayfa" düğmesi çalışıyor.** Arama yaptıktan sonra "Ana sayfa"ya tıklamak
> arama sonuçlarını tekrar gösteriyordu; artık gerçekten ana sayfaya dönüyor.
>
> **"Bölüme git" kutusu düzeltildi.** Artık tüm sezonlarda arıyor ve aynı numarada
> birden fazla bölüm varsa hangilerinin olduğunu söylüyor.
>
> **Google Drive bağlantılarındaki bozuk adres düzeltildi** (1.471 adet).
>
> **Çok sayıda küçük hata giderildi:** Arama sonuçlarında sıralama artık çalışıyor,
> kategori sayıları doğru, "kopyalandı" yazısı yalan söylemiyor, kaldırılan
> bağlantı geri alınabiliyor, kenar listede arama Türkçe karakterleri tanıyor.
>
> **Daha hızlı:** Bazı oynatıcılar (Yandex Disk) tarayıcıda açılamıyordu; artık
> boş siyah kutu yerine "bu sitede oynatıcıya izin vermiyor, kaynak linkini aç"
> mesajı çıkıyor.
>
> **Çökme düzeltmesi:** Bazı ortamlarda site hiç açılmıyordu. Bu hata giderildi.

| | |
|---|---|
| `search.html` | 693.035 → 722.663 B |
| Yeni dosya | `logo.png` (342×104, 55 KB) |
| `kaldirilan.js` | 100 B → 4.432 B (**78 URL**) |
| Veritabanı | `link` tablosu 317.146 → **317.068** (78 ölü satır silindi) |
| Düzeltme | 24+ (4 tur) |
| Test | 63 rota, 0 konsol hatası |

**Doğrulama (kullanıcı isteğiyle 2 kez yapıldı):**

- `kaldirilan.js` → 78 URL, `node` **ve** `json.loads` ile doğrulandı
- `b/` 6.107 dosya tarandı → **0/78** ölü bağlantı kaldı
- `link` tablosu yedekle **küme karşılaştırması**: kalan 317.068 satır birebir
  aynı, kayıp 0, eklenen 0 · `integrity_check` ok · `foreign_key_check` 0 ihlal
- Site tarayıcıda açıldı: 6.107 anime · 71.689 bölüm · **0 konsol hatası**

**Geri alma:**
`git revert` yeterlidir — tüm değişiklikler sürüm kontrolünde.
Ayrıca `b/` için yerel yedek: `b-YEDEK-SILME-ONCESI`, `b-YEDEK-VOE2`.
