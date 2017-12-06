#include <bits/stdc++.h>
 
using namespace std;
#define l long long
 
ifstream fin("dijkstra.in");
ofstream fout("dijkstra.out");
 
const int N = 50005;
const int INF = 1e9;
vector < pair < int, int > > edge[N];
 
bool i_q[N];
int dp[N];
 
struct comp{
    bool operator () (pair <int, int> a, pair <int, int> b){
        return a.first > b.first;
    }
};
 
priority_queue < pair < int, int >, vector < pair < int, int > >, comp > pq;
 
int main(){
    int n, m;
    fin >> n >> m;
    for(int i = 1;i <= m;i++){
        int x, y, c;
        fin >> x >> y >> c;
        edge[x].push_back({y, c});
    }
    for(int i = 1;i <= n;i++){
        dp[i] = INF;
    }
    dp[1] = 0;
    pq.push({0, 1});
    while(pq.empty() == false){
        pair <int, int> node = pq.top();
        pq.pop();
        //in_q[node.second] = false;
        if(in_q[node.second]){
            continue;
        }
        in_q[node.second] = 1;
        for(auto it : edge[node.second]){
            if(dp[it.first] > dp[node.second]+ it.second){
                dp[it.first] = dp[node.second] + it.second;
                //if(in_q[it.first] == false){
                    pq.push({dp[it.first], it.first});
                   //in_q[it.first] = true;
                //}
            }
        }
    }
    for(int i = 2;i <= n;i++){
        if(dp[i] == INF){
            dp[i] = 0;
        }
        fout << dp[i] << ' ';
    }
    return 0;
}
