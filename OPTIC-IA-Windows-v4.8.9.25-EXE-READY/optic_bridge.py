#!/usr/bin/env python3
import os, sys, time, json, struct, threading, mimetypes, urllib.request, urllib.error, webbrowser
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
ROOT = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0,ROOT)
import toupcam

class Camera:
    def __init__(self):
        self.hcam=None; self.buf=None; self.width=0; self.height=0; self.frame=None; self.total=0; self.name=''; self.lock=threading.Lock(); self.error=''
    @staticmethod
    def cb(event, ctx):
        if event==toupcam.TOUPCAM_EVENT_IMAGE: ctx.pull()
    def start(self):
        cams=toupcam.Toupcam.EnumV2()
        if not cams: raise RuntimeError('No se detectó una cámara ToupTek/UCMOS.')
        c=cams[0]; self.name=c.displayname
        self.hcam=toupcam.Toupcam.Open(c.id)
        if not self.hcam: raise RuntimeError('No fue posible abrir la cámara.')
        self.width,self.height=self.hcam.get_Size()
        stride=toupcam.TDIBWIDTHBYTES(self.width*24)
        self.buf=bytes(stride*self.height)
        self.hcam.StartPullModeWithCallback(Camera.cb,self)
    def pull(self):
        try:
            self.hcam.PullImageV4(self.buf,0,24,0,None)
            stride=toupcam.TDIBWIDTHBYTES(self.width*24)
            # BMP: SDK 24-bit buffer is DIB-compatible. Positive height preserves bottom-up layout.
            filesize=54+len(self.buf)
            header=b'BM'+struct.pack('<IHHI',filesize,0,0,54)
            dib=struct.pack('<IIIHHIIIIII',40,self.width,self.height,1,24,0,len(self.buf),2835,2835,0,0)
            with self.lock:
                self.frame=header+dib+self.buf; self.total+=1
        except Exception as e: self.error=str(e)
    def close(self):
        if self.hcam:
            try:self.hcam.Close()
            except:pass
            self.hcam=None
cam=Camera()
try: cam.start()
except Exception as e: cam.error=str(e)

class H(BaseHTTPRequestHandler):
    def cors(self,ctype='application/json'):
        self.send_header('Content-Type',ctype); self.send_header('Access-Control-Allow-Origin','*'); self.send_header('Cache-Control','no-store')
    def do_OPTIONS(self):
        self.send_response(204); self.send_header('Access-Control-Allow-Origin','*'); self.send_header('Access-Control-Allow-Methods','GET,OPTIONS'); self.end_headers()
    def do_GET(self):
        p=self.path.split('?',1)[0]
        if p in ('/','/app','/index.html'):
            data=open(os.path.join(ROOT,'index.html'),'rb').read(); self.send_response(200); self.cors('text/html; charset=utf-8'); self.send_header('Content-Length',str(len(data))); self.end_headers(); self.wfile.write(data); return
        if p.startswith('/assets/'):
            fp=os.path.normpath(os.path.join(ROOT,p.lstrip('/')))
            if not fp.startswith(os.path.join(ROOT,'assets')) or not os.path.isfile(fp): self.send_error(404); return
            data=open(fp,'rb').read(); ctype=mimetypes.guess_type(fp)[0] or 'application/octet-stream'; self.send_response(200); self.cors(ctype); self.send_header('Content-Length',str(len(data))); self.end_headers(); self.wfile.write(data); return
        if p=='/status':
            body=json.dumps({'ok':bool(cam.hcam and cam.frame),'camera':cam.name,'width':cam.width,'height':cam.height,'frames':cam.total,'error':cam.error}).encode()
            self.send_response(200); self.cors(); self.send_header('Content-Length',str(len(body))); self.end_headers(); self.wfile.write(body); return
        if p=='/frame.bmp':
            with cam.lock: frame=cam.frame
            if not frame: self.send_error(503,'Esperando imagen'); return
            self.send_response(200); self.cors('image/bmp'); self.send_header('Content-Length',str(len(frame))); self.end_headers(); self.wfile.write(frame); return
        self.send_error(404)

    def do_POST(self):
        p=self.path.split('?',1)[0]
        if p!='/api/chat': self.send_error(404); return
        try:
            n=int(self.headers.get('Content-Length','0')); body=self.rfile.read(n)
            req=urllib.request.Request('https://optic-ia-by-medhub-v01-prueba.vercel.app/api/chat',data=body,headers={'Content-Type':'application/json','User-Agent':'OPTIC-IA-LocalBridge/2.4'},method='POST')
            with urllib.request.urlopen(req,timeout=120) as r:
                data=r.read(); status=r.status; ctype=r.headers.get('Content-Type','application/json')
            self.send_response(status); self.cors(ctype); self.send_header('Content-Length',str(len(data))); self.end_headers(); self.wfile.write(data)
        except urllib.error.HTTPError as e:
            data=e.read() or json.dumps({'error':str(e)}).encode(); self.send_response(e.code); self.cors('application/json'); self.send_header('Content-Length',str(len(data))); self.end_headers(); self.wfile.write(data)
        except Exception as e:
            data=json.dumps({'error':'Proxy API: '+str(e)}).encode(); self.send_response(502); self.cors(); self.send_header('Content-Length',str(len(data))); self.end_headers(); self.wfile.write(data)
    def log_message(self,fmt,*args): pass

if __name__=='__main__':
    # En la versión .EXE, abre la interfaz local automáticamente.
    threading.Timer(1.2, lambda: webbrowser.open('http://127.0.0.1:8765/app')).start()
    print('\nOPTIC IA · Puente ToupTek')
    if cam.error: print('ERROR:',cam.error)
    else: print('Cámara:',cam.name,'·',cam.width,'x',cam.height)
    print('OPTIC Bridge v2.7 listo: http://127.0.0.1:8765/app')
    print('Dejá esta ventana abierta mientras uses el microscopio.\n')
    # La web de Vercel abre la vista local del microscopio cuando corresponde.
    try: ThreadingHTTPServer(('127.0.0.1',8765),H).serve_forever()
    except KeyboardInterrupt: pass
    finally: cam.close()
