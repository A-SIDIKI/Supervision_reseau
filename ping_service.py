import subprocess
import platform
import time

class PingService:
    @staticmethod
    def ping(ip_address):
        """
        Effectue un ping vers une adresse IP
        Retourne : (disponible, temps_reponse_ms)
        """
        # Adapter la commande selon l'OS
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        
        # Construction de la commande
        command = ['ping', param, '1', ip_address]
        
        try:
            start_time = time.time()
            result = subprocess.run(command, capture_output=True, text=True, timeout=3)
            end_time = time.time()
            
            temps_reponse = (end_time - start_time) * 1000  # en ms
            
            # Le ping a réussi si le code retour est 0
            if result.returncode == 0:
                return True, round(temps_reponse, 2)
            else:
                return False, None
                
        except subprocess.TimeoutExpired:
            return False, None
        except Exception as e:
            print(f"Erreur: {e}")
            return False, None

# Pour tester directement
if __name__ == '__main__':
    # Tester avec Google
    print("Test ping vers Google (8.8.8.8)")
    disponible, temps = PingService.ping('8.8.8.8')
    if disponible:
        print(f"✅ Disponible - {temps} ms")
    else:
        print("❌ Non disponible")
    
    # Tester avec une IP inexistante
    print("\nTest ping vers une IP inexistante (192.168.999.999)")
    disponible, temps = PingService.ping('192.168.999.999')
    if disponible:
        print(f"✅ Disponible - {temps} ms")
    else:
        print("❌ Non disponible")