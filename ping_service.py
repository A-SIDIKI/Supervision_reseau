import subprocess
import platform
import time
import socket

class PingService:
    
    @staticmethod
    def ping_icmp(ip_address, timeout=1):
        """
        Ping ICMP classique
        Retourne : (disponible, temps_reponse_ms)
        """
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        
        if platform.system().lower() == 'windows':
            command = ['ping', param, '1', '-w', str(timeout * 1000), ip_address]
        else:
            command = ['ping', param, '1', '-W', str(timeout), ip_address]
        
        try:
            start_time = time.time()
            result = subprocess.run(command, capture_output=True, text=True, timeout=timeout + 1)
            end_time = time.time()
            
            if result.returncode == 0:
                temps_reponse = (end_time - start_time) * 1000
                return True, round(temps_reponse, 2)
            return False, None
        except Exception:
            return False, None
    
    @staticmethod
    def ping_tcp(ip_address, port=443, timeout=2):
        """
        Test de connexion TCP sur un port (fallback si ICMP bloqué)
        Par défaut port 443 (HTTPS)
        Retourne : (disponible, temps_reponse_ms)
        """
        try:
            start_time = time.time()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((ip_address, port))
            end_time = time.time()
            sock.close()
            
            if result == 0:
                temps_reponse = (end_time - start_time) * 1000
                return True, round(temps_reponse, 2)
            return False, None
        except Exception:
            return False, None
    
    @staticmethod
    def ping(ip_address):
        """
        Vérifie la disponibilité d'une IP :
        1. Essaie ICMP d'abord
        2. Si ICMP échoue, essaie TCP 443 puis TCP 80
        Retourne : (disponible, temps_reponse_ms)
        """
        # Méthode 1 : ICMP
        disponible, temps = PingService.ping_icmp(ip_address, timeout=1)
        if disponible:
            return True, temps
        
        # Méthode 2 : TCP 443 (HTTPS)
        disponible, temps = PingService.ping_tcp(ip_address, port=443, timeout=2)
        if disponible:
            return True, temps
        
        # Méthode 3 : TCP 80 (HTTP)
        disponible, temps = PingService.ping_tcp(ip_address, port=80, timeout=2)
        if disponible:
            return True, temps
        
        return False, None


# Pour tester directement
if __name__ == '__main__':
    print("=== Test avec Google DNS (8.8.8.8) ===")
    disponible, temps = PingService.ping('8.8.8.8')
    print(f"Résultat: {'✅ Disponible' if disponible else '❌ Non disponible'} - {temps} ms")
    
    print("\n=== Test avec Cloudflare (1.1.1.1) ===")
    disponible, temps = PingService.ping('1.1.1.1')
    print(f"Résultat: {'✅ Disponible' if disponible else '❌ Non disponible'} - {temps} ms")
    
    print("\n=== Test avec ta machine (127.0.0.1) ===")
    disponible, temps = PingService.ping('127.0.0.1')
    print(f"Résultat: {'✅ Disponible' if disponible else '❌ Non disponible'} - {temps} ms")
    
    print("\n=== Détails ICMP vs TCP pour 8.8.8.8 ===")
    icmp_dispo, icmp_temps = PingService.ping_icmp('8.8.8.8')
    print(f"ICMP: {'✅' if icmp_dispo else '❌'} {icmp_temps} ms")
    tcp_dispo, tcp_temps = PingService.ping_tcp('8.8.8.8', 443)
    print(f"TCP 443: {'✅' if tcp_dispo else '❌'} {tcp_temps} ms")