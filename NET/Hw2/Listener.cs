using System;
using System.IO;
using System.Net;
using System.Net.Sockets;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Listener
{
    class Program
    {
        public static void Main(string[] args)
        {
            TcpListener server = null;
            try
            {
                Int32 port = 12345;
                IPAddress localAddress = IPAddress.Parse("127.0.0.1");

                server = new TcpListener(localAddress, port);

                server.Start();

                Byte[] bytes = new Byte[256];
                String data = null;

                while (true)
                {
                    Console.Write("Waiting for a connection...");

                    TcpClient client = server.AcceptTcpClient();
                    Console.WriteLine("Connected!");

                    data = null;

                    NetworkStream stream = client.GetStream();

                    int i;
                    while ((i = stream.Read(bytes, 0, bytes.Length)) != 0)
                    {
                        data = System.Text.Encoding.ASCII.GetString(bytes, 0, i);
                        Console.WriteLine("Server Received: {0}", data);
                        string text = data;
                        if (System.IO.File.Exists(data))
                        {
                            text = System.IO.File.ReadAllText(data);
                        }
                        else if (System.IO.Directory.Exists(data))
                        {
                            text = string.Join("\n", System.IO.Directory.GetFiles(data));
                        } else { text = "Path does not exist."; }

                        byte[] msg = System.Text.Encoding.ASCII.GetBytes(text);
                        stream.Write(msg, 0, msg.Length);
                        Console.WriteLine("Server Sent: {0}", text);
                    }

                    client.Close();
                }
            }
            catch (SocketException e) { Console.WriteLine("SocketException: {0}", e); }
            finally { server.Stop(); }

            Console.WriteLine("\nHit enter to continue...");
            Console.Read();
        }
    }

}
