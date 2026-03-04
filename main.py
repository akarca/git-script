import os
import sys

from fabric import Connection

if not sys.warnoptions:
    import warnings

    warnings.simplefilter("ignore")


def run_remote_setup(ssh_host_alias, remote_path):
    # SSH Config dosyasındaki host ismiyle bağlantı kurar
    # Fabric varsayılan olarak ~/.ssh/config dosyasını okur.
    print(f"--- {ssh_host_alias} hostuna bağlanılıyor... ---")

    try:
        # 'c' objesi config'deki ayarları (User, Hostname, Port, IdentityFile) otomatik alır
        c = Connection(ssh_host_alias)

        # 1. Klasörü oluştur
        print(f"[*] Klasör oluşturuluyor: {remote_path}")
        c.run(f"mkdir -p {remote_path}")

        # 2. Git init
        print("[*] Git repo başlatılıyor...")
        with c.cd(remote_path):
            c.run("git init .")

        # 3. Localdeki hook dosyasını yükle
        local_hook_file = "create-post-update-hook.sh"
        remote_hook_dest = f"{remote_path}/{local_hook_file}"

        if os.path.exists(local_hook_file):
            print(f"[*] {local_hook_file} yükleniyor...")
            c.put(local_hook_file, remote=remote_hook_dest)

            # 4. Çalıştırma izni ver ve execute et
            print("[*] Hook dosyası çalıştırılıyor...")
            with c.cd(remote_path):
                c.run(f"chmod +x {local_hook_file}")
                c.run(f"./{local_hook_file}")
                c.run(f"rm -f {local_hook_file}")

            print("\n--- İşlem başarıyla tamamlandı! ---")

        else:
            print(f"\n[!] Hata: Yerelde '{local_hook_file}' dosyası bulunamadı.")
        
        with c.cd(remote_path):
            c.run("git config receive.denyCurrentBranch ignore")

    except Exception as e:
        print(f"\n[!] Bağlantı veya komut hatası: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: main.py <host> <repo_path>")
        sys.exit(1)

    run_remote_setup(sys.argv[1], sys.argv[2])
