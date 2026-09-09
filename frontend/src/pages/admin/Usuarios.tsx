import { useEffect, useState, type FormEvent } from "react";
import {
  atualizarUsuario,
  criarUsuario,
  listarUsuarios,
  redefinirSenha,
} from "../../services/usuarioApi";
import type { PerfilUsuario, Usuario } from "../../types/usuario";

const NOVO_USUARIO_INICIAL = {
  nome: "",
  login: "",
  email: "",
  senha: "",
  perfil: "tecnico" as PerfilUsuario,
};

export function Usuarios() {
  const [usuarios, setUsuarios] = useState<Usuario[]>([]);
  const [erro, setErro] = useState<string | null>(null);
  const [novoUsuario, setNovoUsuario] = useState(NOVO_USUARIO_INICIAL);
  const [senhaRedefinicao, setSenhaRedefinicao] = useState<Record<number, string>>({});

  function carregar() {
    listarUsuarios()
      .then(setUsuarios)
      .catch(() => setErro("Não foi possível carregar os usuários."));
  }

  useEffect(carregar, []);

  async function handleErro(acao: () => Promise<unknown>): Promise<boolean> {
    setErro(null);
    try {
      await acao();
      carregar();
      return true;
    } catch (err) {
      const mensagem =
        (err as { response?: { data?: { detail?: string } } }).response?.data?.detail ??
        "Não foi possível executar a ação.";
      setErro(mensagem);
      return false;
    }
  }

  async function criar(e: FormEvent) {
    e.preventDefault();
    const sucesso = await handleErro(() => criarUsuario(novoUsuario));
    if (sucesso) setNovoUsuario(NOVO_USUARIO_INICIAL);
  }

  return (
    <div>
      <h1>Usuários administrativos</h1>
      {erro && <p className="form-error">{erro}</p>}

      <div className="card">
        <h3>Novo usuário</h3>
        <form onSubmit={criar} className="filtros">
          <input
            placeholder="Nome"
            required
            value={novoUsuario.nome}
            onChange={(e) => setNovoUsuario((u) => ({ ...u, nome: e.target.value }))}
          />
          <input
            placeholder="Login"
            required
            pattern="[a-zA-Z0-9._-]{3,50}"
            title="3 a 50 caracteres: letras, números, ponto, hífen ou underscore"
            value={novoUsuario.login}
            onChange={(e) => setNovoUsuario((u) => ({ ...u, login: e.target.value }))}
          />
          <input
            placeholder="E-mail"
            type="email"
            required
            value={novoUsuario.email}
            onChange={(e) => setNovoUsuario((u) => ({ ...u, email: e.target.value }))}
          />
          <input
            placeholder="Senha (mín. 8 caracteres)"
            type="password"
            required
            minLength={8}
            value={novoUsuario.senha}
            onChange={(e) => setNovoUsuario((u) => ({ ...u, senha: e.target.value }))}
          />
          <select
            value={novoUsuario.perfil}
            onChange={(e) => setNovoUsuario((u) => ({ ...u, perfil: e.target.value as PerfilUsuario }))}
          >
            <option value="tecnico">Técnico</option>
            <option value="administrador">Administrador</option>
          </select>
          <button type="submit">Criar</button>
        </form>
      </div>

      <table>
        <thead>
          <tr>
            <th>Nome</th>
            <th>Login</th>
            <th>E-mail</th>
            <th>Perfil</th>
            <th>Status</th>
            <th>Ações</th>
          </tr>
        </thead>
        <tbody>
          {usuarios.map((u) => (
            <tr key={u.id}>
              <td>{u.nome}</td>
              <td>{u.login}</td>
              <td>
                <input
                  key={u.email}
                  type="email"
                  defaultValue={u.email}
                  style={{ width: 200 }}
                  onBlur={(e) => {
                    const novoEmail = e.target.value.trim();
                    if (novoEmail && novoEmail !== u.email) {
                      handleErro(() => atualizarUsuario(u.id, { email: novoEmail }));
                    }
                  }}
                />
              </td>
              <td>
                <select
                  value={u.perfil}
                  onChange={(e) =>
                    handleErro(() =>
                      atualizarUsuario(u.id, { perfil: e.target.value as PerfilUsuario })
                    )
                  }
                >
                  <option value="tecnico">Técnico</option>
                  <option value="administrador">Administrador</option>
                </select>
              </td>
              <td>
                <span className="badge">{u.ativo ? "Ativo" : "Inativo"}</span>
              </td>
              <td style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
                <button
                  className={u.ativo ? "perigo" : ""}
                  onClick={() => handleErro(() => atualizarUsuario(u.id, { ativo: !u.ativo }))}
                >
                  {u.ativo ? "Desativar" : "Ativar"}
                </button>
                <input
                  placeholder="Nova senha"
                  type="password"
                  style={{ width: 120 }}
                  value={senhaRedefinicao[u.id] ?? ""}
                  onChange={(e) =>
                    setSenhaRedefinicao((s) => ({ ...s, [u.id]: e.target.value }))
                  }
                />
                <button
                  className="secundario"
                  disabled={(senhaRedefinicao[u.id]?.length ?? 0) < 8}
                  onClick={async () => {
                    const sucesso = await handleErro(() =>
                      redefinirSenha(u.id, senhaRedefinicao[u.id])
                    );
                    if (sucesso) setSenhaRedefinicao((s) => ({ ...s, [u.id]: "" }));
                  }}
                >
                  Redefinir senha
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
