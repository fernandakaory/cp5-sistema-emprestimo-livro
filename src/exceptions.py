class BibliotecaError(Exception):
    """Exceção base do domínio."""


class LivroNaoEncontrado(BibliotecaError):
    pass


class AlunoNaoEncontrado(BibliotecaError):
    pass


class LivroIndisponivel(BibliotecaError):
    pass


class LimiteEmprestimos(BibliotecaError):
    pass


class AlunoComAtraso(BibliotecaError):
    pass


class EmprestimoNaoEncontrado(BibliotecaError):
    pass


class EmprestimoJaDevolvido(BibliotecaError):
    pass


class LivroComEmprestimoAberto(BibliotecaError):
    pass


class DadoInvalido(BibliotecaError):
    pass
