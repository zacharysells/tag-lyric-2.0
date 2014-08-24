#include <string>
#include <cstdio>

using namespace std;


void str_format_str(string &s)
{
	for(int i = 0; i < s.size(); i++)
	{
		//Characters to be removed from song title
		if( s[i] == ',' || s[i] == ',' || s[i] == '.' || s[i] == '`' || s[i] == '/' || s[i] == '?' ||
			s[i] == '\'' || s[i] == '!')
		{
			s.erase(i, 1);
		}
		
		else if(s[i] == '&') //Special case for ampersand
		{
			s.erase((i-1),2);
		}
		
		else if(s[i] == ' ') // Replace spaces(' ') with dashes('-')
		{
			s[i] = '-';
		}
		
		else if(s[i] == '(') //Special case for parenthesis
		{
			for(int e = s.find('('); e < s.size(); e++)
			{
				if( s[e] == ',' || s[e] == ',' || s[e] == '.' || s[e] == '`' || s[e] == '/' || s[e] == '?' ||
				s[e] == '\'' )
				{
					s.erase(e, 1);
				}
				
				else if(s[e] == '&')
				{
					s.erase((e-1),2);
				}
				
				else if(s[e] == ' ') 
				{
					s[e] = '-';
				}
				
				else if(s[e] == ')') 
				{
					s.erase(e,1);
				}
			}
			s[i] = '-';
			break;
		}
	}	
}

string to_lower(const string &str)
{
	string lower_case_str = str;
	for(int i = 0; i < str.size(); ++i)
	{
		// Character is upper case
		if(str[i] >= 65 && str[i] <= 90)
		{
			// Convert to lower case
			lower_case_str[i] = str[i] + 32;
		}
	}
	return lower_case_str;
}

int main(int argc, char* argv[])
{
	if(argc != 2)
	{
		printf("Incorrect number of arguments. -h for usage");
		return 0;
	}
	
	string str(argv[1]);
	str = to_lower(str);
	str_format_str(str);
	
	
	printf("%s", str.c_str());
}

