using HtmlAgilityPack;
using System;
using System.Linq;
using System.Net.Http;
using System.Threading.Tasks;


namespace WebCrawler
{
    class Program
    {
        static void Main(string[] args)
        {
            startCrawlerAsync();
            Console.ReadLine();
        }

        private static async Task startCrawlerAsync()
        {
            var url = "https://letterboxd.com/crew/list/most-fans-per-viewer-on-letterboxd/detail/";
            var httpClient = new HttpClient();
            var html = await httpClient.GetStringAsync(url);
            var htmlDocument = new HtmlDocument();
            htmlDocument.LoadHtml(html);
            var movieList = htmlDocument.DocumentNode.SelectSingleNode("//div/div/div/section/ul");
            var title = htmlDocument.DocumentNode.SelectSingleNode("//div/div/div/section/div[2]/h1");
            var published = htmlDocument.DocumentNode.SelectSingleNode("//p/span/time");
            var creator = htmlDocument.DocumentNode.SelectSingleNode("//div/div/div/section/header/div/h1/a/text()");
            foreach (var entry in movieList.Descendants("li"))
            {
                if (entry.NodeType == HtmlNodeType.Element)
                {
                    var film = new Film
                    {
                        Rank = Int32.Parse(entry.Descendants("div").LastOrDefault().Descendants("span").LastOrDefault().InnerText.Replace('.', ' ').Trim()),
                        Title = System.Net.WebUtility.HtmlDecode(entry.Descendants("div").LastOrDefault().Descendants("a").FirstOrDefault().InnerText),
                        Year = Int32.Parse(entry.Descendants("div").LastOrDefault().Descendants("small").LastOrDefault().InnerText)
                    };
                    Console.WriteLine(film.ToString());
                }
            }
        }
    }
}
