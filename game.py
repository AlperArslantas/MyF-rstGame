import pgzrun
from pgzero.actor import Actor
from pgzero.clock import schedule_interval
from pgzero.rect import Rect
import random

collectibles = []  # Toplanabilir nesnelerin listesi
# Skor
score = 0
# Toplanabilir nesneleri rastgele konumda oluştur
def create_collectible():
    x = random.randint(50, 750)
    y = random.randint(50, 420)
    collectible = Actor("coin", (x, y))
    collectibles.append(collectible)




background = Actor('background', topleft=(0, 0))  # Arka plan görselini yükle


# Oyun ayarları
WIDTH = 800
HEIGHT = 600

# Oyun durumu
game_state = "menu"
music_on = True
# Zaman sayacı değişkenleri
remaining_time = 60  # Oyun süresi (saniye)
game_active = False  # Oyunun aktif olup olmadığını kontrol eder
# Actor'ları oluştur
hero = Actor('hero_idle', center=(WIDTH//2, HEIGHT//2))
enemies = [Actor('enemy_idle', center=(50, 50)), Actor('enemy_idle', center=(750, 550))]
hero.vy = 0  # Karakterin dikey hızını takip eder
gravity = 0.5  # Yerçekimi
is_jumping = False




# Platformları tanımla
platforms = [
    # Ana zemin platformları (alt iki parça)
    Rect((0, HEIGHT-195), (295, 180)),      # Sol ana zemin - hafif yükseltilmiş
    Rect((500, HEIGHT-195), (395, 180)),    # Sağ ana zemin - sol ile uyumlu olarak yükseltilmiş

    # Yüzen platformlar (çimen parçaları)
    Rect((110, HEIGHT-360), (65, 40)),      # Sol alt platform (ahşap tabelanın yanındaki)
    Rect((225, HEIGHT-480), (145, 30)),     # Sol üst büyük platform
    Rect((440, HEIGHT-380), (65, 30)),     # Orta küçük platform
    Rect((580, HEIGHT-455), (150, 30)),     # Sağ üst platform
]

# Kahraman animasyonu için resimleri tanımla
hero_walk_left= ['hero_walk_left_1.png', 'hero_walk_left_2.png', 'hero_walk_left_3.png']
hero_walk_right= ['hero_walk_right_1.png', 'hero_walk_right_2.png', 'hero_walk_right_3.png']

enemy_walk_right =['enemy_walk_right_1 .png','enemy_walk_right_2.png' , 'enemy_walk_right_3.png']
enemy_walk_left =['enemy_walk_left_1.png','enemy_walk_left_2.png' , 'enemy_walk_left_3.png']

# Kahraman animasyonları
hero_anim_frame = 0  # Animasyon karesi
hero_anim_speed = 0.1  # Animasyon hızı (her 0.1 saniyede bir kare değiştirecek)

# Düşman animasyonları (her bir düşman için ayrı bir animasyon karesi)
enemy_anim_frame = [0, 0]  # Her düşman için ayrı animasyon karesi
enemy_anim_speed = 0.1



# Kahramanın başlangıç pozisyonu (ilk bloğun üstü)
hero.x = platforms[0].x + platforms[0].width // 2
hero.y = platforms[0].y - hero.height // 2

# Başlangıç pozisyonu
hero_start_position = (platforms[0].x + platforms[0].width // 2, platforms[0].y - hero.height // 2)
# Zamanı azaltma fonksiyonu

def decrease_time():
    global remaining_time, game_state
    if game_state == "game" and remaining_time > 0:
        remaining_time -= 1
        if remaining_time <= 0:
            game_over()



# Düğme sınıfı
class Button:
    def __init__(self, text, x, y, action):
        self.text = text
        self.x = x
        self.y = y
        self.action = action
        self.width = 200
        self.height = 50

    def draw(self):
        screen.draw.text(self.text, center=(self.x, self.y), fontsize=50, color="white")

    def check_click(self, pos):
        if (self.x - self.width/2 < pos[0] < self.x + self.width/2 and
            self.y - self.height/2 < pos[1] < self.y + self.height/2):
            try:
                sounds.click.play()  # Sadece tıklama sesi
            except:
                pass
            self.action()

# Düğme fonksiyonları
def start_game():
    global game_state, remaining_time, game_active
    game_state = "game"
    game_active = True
    remaining_time = 60
      # Müzik çalmasını başlat ve döngüde çalsın
    if music_on:
        try:
            music.stop()  # Önceki müziği durdur
            music.play('background_music.wav') 
            music.set_volume(0.5)
            print("Müzik çalınmaya başladı")
        except Exception as e:
            print(f"Müzik çalma hatası: {e}")


def toggle_music():
    global music_on
    music_on = not music_on
    try:
        if music_on:
            music.play('background_music.wav')
            print("Müzik açıldı")
        else:
            music.stop()
            print("Müzik kapatıldı")
    except Exception as e:
        print(f"Müzik işlemi hatası: {e}")

def exit_game():
    quit()

# Düğmeleri oluştur
start_button = Button("Oyuna Başla", WIDTH//2, HEIGHT//2 - 50, start_game)
music_button = Button("Müzik Aç/Kapat", WIDTH//2, HEIGHT//2, toggle_music)
exit_button = Button("Çıkış", WIDTH//2, HEIGHT//2 + 50, exit_game)


# Düşman hareketi ve animasyonu
def move_enemies():
    for i, enemy in enumerate(enemies):
        # Düşmanın hareket yönünü kontrol et
        if enemy.x < hero.x:
            enemy.image = enemy_walk_right[int(enemy_anim_frame[i])]  # Düşman sağa doğru yürüyor
            enemy.x += 2  # Sağ hareket
        else:
            enemy.image = enemy_walk_left[int(enemy_anim_frame[i])]  # Düşman sola doğru yürüyor
            enemy.x -= 2  # Sol hareket
         # Her bir düşman için sabit y koordinatı
        if i == 0:
            enemy.y = 100  # İlk düşman için sabit y değeri
        elif i == 1:
            enemy.y = 370  # İkinci düşman için sabit y değeri

        # Animasyonu güncelle
        enemy_anim_frame[i] += enemy_anim_speed
        if enemy_anim_frame[i] >= len(enemy_walk_right):  # Animasyon döngüsünü tekrar başlat
            enemy_anim_frame[i] = 0

schedule_interval(move_enemies, 0.05)

# Kaybetme kontrolü
def check_game_over():
    # Kahraman, düşmanlardan birine çarptıysa veya ekrandan düştüyse oyun biter
    for enemy in enemies:
        if hero.colliderect(enemy):
            return True
    if hero.y > HEIGHT:  # Kahraman düşerse
        return True
    return False

# Oyun Sonu durumu
def game_over():
    global game_state ,game_active
    game_state = "game_over"
    game_active = False

# Oyunu yeniden başlatırken score'u sıfırla
def restart_game():
    global game_state, hero, enemies, score, collectibles, remaining_time, game_active
    game_state = "game"
    hero = Actor('hero_idle', center=hero_start_position)
    enemies = [Actor('enemy_idle', center=(50, 200)), Actor('enemy_idle', center=(750, 400))]
    score = 0
    remaining_time = 60  # Zamanı resetle
    game_active = True  # Oyunu aktif et
    collectibles.clear()  # Mevcut coin'leri temizle
    for _ in range(5):  # Yeni coin'ler oluştur
        create_collectible()

# Kazanma kontrolü
def check_game_win():
    if hero.x > WIDTH - 50:  # Kahraman ekranın sağ tarafına geldiğinde
        for platform in platforms:
            if hero.colliderect(platform):  # Eğer bir platformun üstündeyse
                return True
    return False

# Kazanma durumu
def game_win():
    global game_state
    game_state = "game_win"


# Fizik değişkenleri
gravity = 1  # Yerçekimi hızı
jump_strength = -15  # Zıplama gücü
vertical_velocity = 0  # Dikey hız

def update():
    global hero_anim_frame, enemy_anim_frame, vertical_velocity,score  # global değişkenler

    if game_state == "game":
        if keyboard.left:
            hero.x = max(0, hero.x - 5)
            hero.image = hero_walk_left[int(hero_anim_frame)]  # Sol yürüme animasyonu
        elif keyboard.right:
            hero.x = min(WIDTH, hero.x + 5)
            hero.image = hero_walk_right[int(hero_anim_frame)]  # Sağ yürüme animasyonu
        else:
            hero.image = 'hero_idle'  # Durma animasyonu

        # Animasyon çerçevesini güncelle
        hero_anim_frame += hero_anim_speed
        if hero_anim_frame >= len(hero_walk_left):  # Animasyon döngüsünü tekrar başlat
            hero_anim_frame = 0

        # Düşman hareketi ve animasyonu
        for i, enemy in enumerate(enemies):
            if enemy.x < hero.x:
                enemy.image = enemy_walk_right[int(enemy_anim_frame[i])]  # Düşman sağa doğru yürüyor
            else:
                enemy.image = enemy_walk_left[int(enemy_anim_frame[i])]  # Düşman sola doğru yürüyor

            # Animasyonu güncelle
            enemy_anim_frame[i] += enemy_anim_speed
            if enemy_anim_frame[i] >= len(enemy_walk_right):  # Animasyon döngüsünü tekrar başlat
                enemy_anim_frame[i] = 0

        # Yerçekimi uygulama
        vertical_velocity += gravity
        hero.y += vertical_velocity

        # Çarpışma kontrolü (platformlarla)
        on_ground = False
        for platform in platforms:
            if hero.colliderect(platform) and vertical_velocity >= 0:  # Düşerken kontrol
                hero.y = platform.y - hero.height // 2  # Bloğun üstüne yerleştir
                vertical_velocity = 0  # Hızı sıfırla
                on_ground = True
        
         # Coin toplama kontrolü
        for collectible in collectibles[:]:  # [:] ile listeyi kopyalayarak döngüye gir
            if hero.colliderect(collectible):  # player yerine hero kullan
                collectibles.remove(collectible)
                score += 10
                try:
                    sounds.coin.play()  # Eğer coin sesi varsa çal
                except:
                    pass
                
                # Yeni coin oluştur
                create_collectible()
        

        # Zıplama
        if keyboard.up and on_ground:
            vertical_velocity = jump_strength

        # Oyun sonu kontrolü
        if check_game_over():
            game_over()

        # Kazanma kontrolünü doğru bir şekilde çağır
        if check_game_win():
            game_win()




def on_key_down(key):
    global is_jumping

    # Zıplama
    if key == keys.SPACE and not is_jumping:
        is_jumping = True
        hero.vy = -10  # Zıplama gücü
            

def on_mouse_down(pos):
    if game_state == "menu":
        start_button.check_click(pos)
        music_button.check_click(pos)
        exit_button.check_click(pos)
    elif  game_state == "game_over" or game_state == "game_win":
        # Yeniden başlatma butonuna tıklanırsa
        if WIDTH//2 - 100 < pos[0] < WIDTH//2 + 100 and HEIGHT//2 + 50 < pos[1] < HEIGHT//2 + 150:
            restart_game()

def draw():
    screen.clear()
    screen.blit("background", (0, 0))  # Arka planı çiz

    if game_state == "menu":
        start_button.draw()
        music_button.draw()
        exit_button.draw()
    elif game_state == "game":
        # Kahramanı çiz
        hero.draw()
        #Düşmanı çiz
        for enemy in enemies:
            enemy.draw()
       # Coin'leri çiz
        for collectible in collectibles:
            collectible.draw()            
     # Skor ve zamanı göster
        screen.draw.text(f"Score: {score}", (30, 30), fontsize=40, color="white")
        screen.draw.text(f"Time: {remaining_time}", (WIDTH-150, 30), fontsize=40, color="white")
         # Süre az kaldığında uyarı
        if remaining_time <= 10:
            screen.draw.text("TIME IS RUNNING OUT!", center=(WIDTH//2, 50), 
                           fontsize=40, color="red")
        
    elif game_state == "game_over":
        # Game Over yazısını yukarı çek
        screen.draw.text("Game Over", center=(WIDTH//2, HEIGHT//2 - 60), 
                        fontsize=60, color="red")
        
        # Final Score yazısını tam ortaya koy
        screen.draw.text(f"Final Score: {score}", center=(WIDTH//2, HEIGHT//2), 
                        fontsize=40, color="white")
        
        # Yeniden Başla yazısını aşağıda tut
        screen.draw.text("Yeniden Başla", center=(WIDTH//2, HEIGHT//2 + 60), 
                        fontsize=50, color="white")

    elif game_state == "game_win":
        # You Win! yazısını yukarı çek
        screen.draw.text("You Win!", center=(WIDTH//2, HEIGHT//2 - 60), 
                        fontsize=60, color="green")
        
        # Final Score yazısını tam ortaya koy
        screen.draw.text(f"Final Score: {score}", center=(WIDTH//2, HEIGHT//2), 
                        fontsize=40, color="white")
        
        # Yeniden Başla yazısını aşağıda tut
        screen.draw.text("Yeniden Başla", center=(WIDTH//2, HEIGHT//2 + 60), 
                        fontsize=50, color="white")

def init():
    print("Müzik yükleniyor...")
    try:
        music.play('background_music.wav') 
        music.set_volume(0.5)
        print("Müzik Çalıyor")
    except Exception as e:
        print(f"Müzik başlatma hatası: {e}")
    
      # Başlangıçta 5 coin oluştur
    for _ in range(5):
        create_collectible()
     # Zamanlayıcıyı başlat
    schedule_interval(decrease_time, 1.0)

init()
pgzrun.go()