import { useEffect, useState, type FormEvent } from "react";
import {
  obterConfiguracaoSmtp,
  salvarConfiguracaoSmtp,
  testarConfiguracaoSmtp,
} from "../../services/configuracaoApi";

const FORM_INICIAL = {
  host: "",
  port: 587,
  usuario: "",
  remetente: "",
  senha: "",
};

function mensagemErro(err: unknown, padrao: string): string {
  return (
    (err as { response?: { data?: { detail?: string } } }).response?.data?.detail ?? padrao
  );
}

export function Configuracoes() {
  const [form, setForm] = useState(FORM_INICIAL);
  const [senhaConfigurada, setSenhaConfigurada] = useState(false);
  const [erro, setErro] = useState<string | null>(null);
  const [sucesso, setSucesso] = useState<string | null>(null);
  const [salvando, setSalvando] = useState(false);
  const [destinatarioTeste, setDestinatarioTeste] = useState("");
  const [testando, setTestando] = useState(false);

  useEffect(() => {
    obterConfiguracaoSmtp()
      .then((config) => {
        if (config) {
          setForm({
            host: config.host,
            port: config.port,
            usuario: config.usuario,
            remetente: config.remetente,
            senha: "",
          });
          setSenhaConfigurada(config.senha_configurada);
        }
      })
      .catch(() => setErro("Não foi possível carregar a configuração de SMTP."));
  }, []);

  async function salvar(e: FormEvent) {
    e.preventDefault();
    setErro(null);
    setSucesso(null);
    setSalvando(true);
    try {
      const config = await salvarConfiguracaoSmtp({
        host: form.host,
        port: form.port,
        usuario: form.usuario,
        remetente: form.remetente,
        senha: form.senha || undefined,
      });
      setSenhaConfigurada(config.senha_configurada);
      setForm((f) => ({ ...f, senha: "" }));
      setSucesso("Configuração salva com sucesso.");
    } catch (err) {
      setErro(mensagemErro(err, "Não foi possível salvar a configuração."));
    } finally {
      setSalvando(false);
    }
  }

  async function enviarTeste() {
    setErro(null);
    setSucesso(null);
    setTestando(true);
    try {
      await testarConfiguracaoSmtp(destinatarioTeste);
      setSucesso(`E-mail de teste enviado para ${destinatarioTeste}.`);
    } catch (err) {
      setErro(mensagemErro(err, "Não foi possível enviar o e-mail de teste."));
    } finally {
      setTestando(false);
    }
  }

  return (
    <div>
      <h1>Configurações</h1>
      {erro && <p className="form-error">{erro}</p>}
      {sucesso && <p className="form-sucesso">{sucesso}</p>}

      <div className="card">
        <h3>Servidor de e-mail (SMTP)</h3>
        <p>
          Usado para enviar login e senha ao médico após a aprovação da solicitação.
          {senhaConfigurada && " Uma senha já está configurada — deixe o campo em branco para mantê-la."}
        </p>
        <form onSubmit={salvar} className="filtros">
          <input
            placeholder="Host (ex: smtp.gmail.com)"
            required
            value={form.host}
            onChange={(e) => setForm((f) => ({ ...f, host: e.target.value }))}
          />
          <input
            placeholder="Porta"
            type="number"
            required
            min={1}
            max={65535}
            style={{ width: 100 }}
            value={form.port}
            onChange={(e) => setForm((f) => ({ ...f, port: Number(e.target.value) }))}
          />
          <input
            placeholder="Usuário"
            value={form.usuario}
            onChange={(e) => setForm((f) => ({ ...f, usuario: e.target.value }))}
          />
          <input
            placeholder={senhaConfigurada ? "Senha (deixe em branco para manter)" : "Senha"}
            type="password"
            value={form.senha}
            onChange={(e) => setForm((f) => ({ ...f, senha: e.target.value }))}
          />
          <input
            placeholder="E-mail remetente"
            type="email"
            required
            value={form.remetente}
            onChange={(e) => setForm((f) => ({ ...f, remetente: e.target.value }))}
          />
          <button type="submit" disabled={salvando}>
            {salvando ? "Salvando..." : "Salvar"}
          </button>
        </form>
      </div>

      <div className="card">
        <h3>Testar envio</h3>
        <form
          className="filtros"
          onSubmit={(e) => {
            e.preventDefault();
            enviarTeste();
          }}
        >
          <input
            placeholder="E-mail de destino"
            type="email"
            required
            value={destinatarioTeste}
            onChange={(e) => setDestinatarioTeste(e.target.value)}
          />
          <button type="submit" className="secundario" disabled={testando}>
            {testando ? "Enviando..." : "Enviar e-mail de teste"}
          </button>
        </form>
      </div>
    </div>
  );
}
