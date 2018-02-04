// gcc final_shell.c -o shell -lreadline

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <unistd.h>
#include <limits.h>
#include <fcntl.h>
#include <dirent.h>

#include <readline/readline.h>
#include <readline/history.h>

#include <sys/types.h>
#include <sys/wait.h>

#define SPLITLINE_BUFFER 128
#define SPLITLINE_TOKENS " \t\r\n\f\v"

int shell_cd(char **args);
int shell_mv(char **args);
int shell_rm(char **args);
int shell_dir(char **args);
int shell_help();
int shell_version();
int shell_exit(char **args);
int shell_builtins_count();

void shell_loop();
char *shell_readline();
char **shell_splitline(char *line);
int shell_exec(char **args);
void destination(int pipefd[], char **args2);
void source(int pipefd[], char **args);

mode_t mode = S_IRUSR | S_IRGRP | S_IWGRP | S_IWUSR;

char *builtins[] = {
	"cd",
	"mv",
	"rm",
	"dir",
	"help",
	"version",
	"exit"
};

char *redirection[] = {
	">",
	"|"
};

int (*builtin_func[]) (char **) = {
	&shell_cd,
	&shell_mv,
	&shell_rm,
	&shell_dir,
	&shell_help,
	&shell_version,
	&shell_exit
};

int shell_builtins_count() {
	return sizeof(builtins) / sizeof(char *);
}

int argSize(char **args)
{
	int i = 0, len = 0;
	for (i = 0; args[i] != NULL; i++)
		len++;
	return len;
}

void shell_loop()
{
	char *line;
	char **args;
	int status;

	do {
		line = shell_readline();
		args = shell_splitline(line);
		status = shell_exec(args);
		free(line);
		free(args);
	} while(status);
}

char *shell_readline()
{
	char *line = NULL;
	char *buf;
	ssize_t buffer = 0;
	buf = readline("> ");
	if (buf[0])
		add_history(buf);
	return buf;
}

char **shell_splitline(char *line)
{
	int buffer = SPLITLINE_BUFFER, idx = 0;
	char **tokens = malloc(buffer * sizeof(char*));
	char *token;

	if (!tokens)
       	{
		fprintf(stderr, "error while allocating memory\n");
		exit(EXIT_FAILURE);
	}

	token = strtok(line, SPLITLINE_TOKENS);
	while (token != NULL)
	{
		tokens[idx++] = token;

		if(idx >= buffer)
		{
			buffer += SPLITLINE_BUFFER;
			tokens = realloc(tokens, buffer * sizeof(char*));

			if (!tokens)
			{
				fprintf(stderr, "error while allocating memory\n");
				exit(EXIT_FAILURE);
			}
		}
		token = strtok(NULL, SPLITLINE_TOKENS);
	}
	tokens[idx] = NULL;
	return tokens;
}

int shell_launch(char **args)
{
	pid_t pid, wait;
	int status;
	int len = 0, i = 0;
	int s_output = 0, s_pipe = 0;
	int in, out;

	len = argSize(args);

	for (i = 0; i < len; i++) {
		if (strcmp(args[i], redirection[0]) == 0)
			s_output = i;
		else if (strcmp(args[i], redirection[1]) == 0)
			s_pipe = i;
	}

	if (s_output == 0 && s_pipe == 0)
	{
		pid = fork();
		if (!pid) // CHILD
		{
			if (execvp(args[0], args) == -1) {
				perror(args[0]);
				exit(EXIT_FAILURE);
			}
		}
		else if (pid < 0) // ERROR
			perror("fork");
		else // PARENT
			do {
				wait = waitpid(pid, &status, WUNTRACED);
			} while (!WIFEXITED(status) && !WIFSIGNALED(status));
		return 1;
	}

	else if (s_output > 0 && s_pipe == 0)
	{
		pid = fork();
		if (!pid) // CHILD - redirection
		{
			args[s_output] = NULL;
			out = open(args[++s_output], O_WRONLY | O_TRUNC | O_CREAT, mode);
			dup2(out, STDOUT_FILENO);
			close(out);

			if (execvp(args[0], args) == -1) {
				perror("execvp");
				exit(EXIT_FAILURE);
			}
		}
		else if (pid < 0) // ERROR
			perror("fork");
		else // PARENT
			do {
				wait = waitpid(pid, &status, WUNTRACED);
			} while (!WIFEXITED(status) && !WIFSIGNALED(status));
		return 1;
	}

	else if (s_pipe > 0)
	{
		int status;
		int fd[2];
		int j = 0, k = 1;

		char **args2 = malloc((len - s_pipe) * sizeof(char *));
		if (!args2)
		{
			fprintf(stderr, "error while allocating memory\n");
			exit(EXIT_FAILURE);
		}

		do { //right of pipe
			args2[j++] = args[s_pipe + k++];
		} while (j < len - s_pipe - 1);
		args2[j] = NULL;
		args[s_pipe] = NULL;

		pipe(fd);

		source(fd, args);
		destination(fd, args2);
		close(fd[0]);
		close(fd[1]);
	}
	return 1;
}

//redirection
void source(int pipefd[], char **args)
{
	pid_t pid, wait;
	int status;
	int len = 0, i = 0;
	int in;

	len = argSize(args);

	pid = fork();
	if (!pid) // CHILD
	{
		dup2(pipefd[1], STDOUT_FILENO);
		if (execvp(args[0], args) == -1) {
			perror("source execvp");
			exit(EXIT_FAILURE);
		}
	}
	else if (pid < 0) // ERROR
		perror("source fork");
	else {// PARENT
		close(pipefd[1]);
		do {
			wait = waitpid(pid, &status, WUNTRACED);
		} while (!WIFEXITED(status) && !WIFSIGNALED(status));
	}
}

void destination(int pipefd[], char **args2)
{
	pid_t pid, wait;
	int status;
	int len = 0, i = 0;
	int s_output;
	int out;

	len = argSize(args2);
	for (i = 0; i < len; i++)
		if (strcmp(args2[i], redirection[0]) == 0)
			s_output = i;

	pid = fork();
	if (!pid) // CHILD
	{
		if (s_output > 0) {
			out = open(args2[++s_output], O_WRONLY | O_TRUNC | O_CREAT, mode);
			dup2(out, STDOUT_FILENO);
			close(out);
			args2[s_output] = NULL;
		}

		dup2(pipefd[0], STDIN_FILENO);
		if (execvp(args2[0], args2) == -1) {
			perror("destination execvp");
			exit(EXIT_FAILURE);
		}
	}
	else if (pid < 0) // ERROR
		perror("destination fork");
	else // PARENT
		do {
			wait = waitpid(pid, &status, WUNTRACED);
		} while (!WIFEXITED(status) && !WIFSIGNALED(status));
}

int shell_exec(char **args)
{
	int i;
	if (args[0] == NULL)
		return 1;

	for (i = 0; i < shell_builtins_count(); i++)
		if (strcmp(args[0], builtins[i]) == 0)
			return (*builtin_func[i])(args);

	return shell_launch(args);
}


// builtin implementations
int shell_cd(char **args)
{
	if (args[1] == NULL) {
		fprintf(stderr, "no argument provided for cd\n");
	} else {
		if (!chdir(args[1])) {
			char cwd[1024];
  		if (getcwd(cwd, sizeof(cwd)) != NULL)
       		fprintf(stdout, "Changed directory to: %s\n", cwd);
   		else
       		perror("getcwd() error");
       }
	}
	return 1;
}

int shell_dir(char **args)
{
	DIR *dp;
	struct dirent *ep;
	dp = opendir ("./");

	if (dp != NULL)
	{
    	while (ep = readdir (dp))
    	puts (ep->d_name);

    	(void) closedir (dp);
  	}
  	else fprintf(stderr, "Couldn't open the directory");
  	return 1;
}

int shell_mv(char **args)
{
	int fd1, fd2;
	int n, count = 0;
	fd1 = open(args[1], O_RDONLY);
	fd2 = creat(args[2], S_IWUSR);
	rename(&fd1, &fd2);
	unlink(args[1]);
	return 1;
}

int shell_rm(char **args)
{
	int status;
	status = remove(args[1]);
	if (status == 0)
		printf("%s file deleted successfully.\n",args[1]);
	else
	{
		printf("Unable to delete the file\n");
		perror("Error");
	}
	return 1;
}

int shell_help()
{
	printf("Available commands\n");
	printf("  cd\n  ls\n  mv\n  rm\n  help\n  version\n  exit\n");
	return 1;
}

int shell_version()
{
	printf("Shell-like application made by Gabriel Nagy as a faculty project");
	printf("\nVersion 0.3\n");
	return 1;
}

int shell_exit(char **args)
{
	return 0;
}

// main
int main(int argc, char **argv)
{
	shell_loop();
	return EXIT_SUCCESS;
}
