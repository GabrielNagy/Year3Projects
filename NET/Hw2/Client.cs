using System;
using System.IO;
using System.Net;
using System.Net.Sockets;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Client
{
    class Program
    {
        static void Connect(String server, String message)
        {
            try
            {
                Int32 port = 12345;
                TcpClient client = new TcpClient(server, port);

                Byte[] data = System.Text.Encoding.ASCII.GetBytes(message);

                NetworkStream stream = client.GetStream();

                stream.Write(data, 0, data.Length);
                Console.WriteLine("Client Sent: {0}", message);

                data = new Byte[256];
                String responseData = String.Empty;
                Int32 bytes = stream.Read(data, 0, data.Length);
                responseData = System.Text.Encoding.ASCII.GetString(data, 0, bytes);
                Console.WriteLine("Client Received: {0}", responseData);

                stream.Close();
                client.Close();
            }
            catch (ArgumentNullException e) { Console.WriteLine("ArgumentNullException: {0}", e); }
            catch (SocketException e) { Console.WriteLine("SocketException: {0}", e); }
            Console.WriteLine("\n Press enter to continue...");
            Console.Read();
        }
        static void Main(string[] args)
        {
            Connect("127.0.0.1", @"C:\a");
        }
    }
}
