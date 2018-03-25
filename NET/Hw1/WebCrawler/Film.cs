using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace WebCrawler
{
    [DebuggerDisplay("{Title}, {Year}")]
    class Film
    {
        public string Title { get; set; }
        public int Year { get; set; }
        public int Rank { get; set; }
        public override string ToString()
        {
            return "Rank: " + Rank.ToString() + ", Title: " + Title.ToString() + ", Release Year: " + Year.ToString();
        }

    }
}
