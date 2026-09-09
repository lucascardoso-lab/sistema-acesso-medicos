import { zodResolver } from "@hookform/resolvers/zod";
import { useState } from "react";
import { Controller, useForm } from "react-hook-form";
import { useNavigate } from "react-router-dom";
import { z } from "zod";
import { criarSolicitacao } from "../../services/solicitacaoApi";
import { UFS } from "../../types/solicitacao";

const EXTENSOES_DOCUMENTO = [".pdf", ".jpg", ".jpeg", ".png"];
const EXTENSOES_FOTO = [".jpg", ".jpeg", ".png"];
const TAMANHO_MAXIMO_BYTES = 5 * 1024 * 1024;

const CONSELHOS = [
  "CRM",
  "CRO",
  "CRN",
  "CRBM",
  "CFF",
  "COREN",
  "CREFITO",
  "CREFONO",
  "CRBio",
  "outros",
] as const;

function extensaoValida(nome: string, extensoes: string[]): boolean {
  const nomeLower = nome.toLowerCase();
  return extensoes.some((ext) => nomeLower.endsWith(ext));
}

function arquivoValido(extensoes: string[]) {
  return z
    .instanceof(File, { message: "Arquivo obrigatório" })
    .refine((f) => f.size > 0, "Arquivo obrigatório")
    .refine((f) => f.size <= TAMANHO_MAXIMO_BYTES, "Arquivo excede o tamanho máximo de 5 MB")
    .refine((f) => extensaoValida(f.name, extensoes), `Extensões aceitas: ${extensoes.join(", ")}`);
}

const schema = z
  .object({
    conselho: z.enum(CONSELHOS, { message: "Selecione o conselho profissional" }),
    conselho_outro: z.string().max(20).optional(),
    nome_completo: z.string().min(3, "Informe o nome completo").max(150),
    numero_conselho: z.string().min(1, "Informe o número do conselho").max(30),
    uf_conselho: z.enum(UFS, { message: "Selecione a UF do conselho" }),
    especialidade: z.string().min(2, "Informe a especialidade").max(100),
    email: z.string().email("E-mail inválido"),
    telefone: z.string().min(8, "Informe um telefone válido").max(20),
    consentimento_lgpd: z.literal(true, {
      message: "É necessário aceitar o tratamento dos dados pessoais",
    }),
    documento: arquivoValido(EXTENSOES_DOCUMENTO),
    foto_documento: arquivoValido(EXTENSOES_FOTO),
  })
  .refine((data) => data.conselho !== "outros" || (data.conselho_outro ?? "").trim().length >= 2, {
    message: "Informe o nome do conselho",
    path: ["conselho_outro"],
  });

type FormValues = z.infer<typeof schema>;

export function SolicitacaoForm() {
  const navigate = useNavigate();
  const [erroEnvio, setErroEnvio] = useState<string | null>(null);
  const {
    register,
    control,
    watch,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) });
  const conselhoSelecionado = watch("conselho");

  async function onSubmit(values: FormValues) {
    setErroEnvio(null);
    try {
      const conselho =
        values.conselho === "outros" ? (values.conselho_outro ?? "").trim() : values.conselho;
      const { protocolo } = await criarSolicitacao({ ...values, conselho });
      navigate("/solicitacao/sucesso", { state: { protocolo } });
    } catch (err) {
      const mensagem =
        (err as { response?: { data?: { detail?: string } } }).response?.data?.detail ??
        "Não foi possível enviar a solicitação. Tente novamente.";
      setErroEnvio(mensagem);
    }
  }

  return (
    <div className="form-container">
      <h1>Solicitação de acesso</h1>
      <p>Preencha seus dados e anexe os documentos solicitados.</p>

      <form onSubmit={handleSubmit(onSubmit)} noValidate>
        <div className="form-field">
          <label htmlFor="nome_completo">Nome completo</label>
          <input id="nome_completo" {...register("nome_completo")} />
          {errors.nome_completo && <span className="form-error">{errors.nome_completo.message}</span>}
        </div>

        <div className="form-row">
          <div className="form-field">
            <label htmlFor="conselho">Conselho</label>
            <select id="conselho" defaultValue="" {...register("conselho")}>
              <option value="" disabled>
                Selecione
              </option>
              {CONSELHOS.map((conselho) => (
                <option key={conselho} value={conselho}>
                  {conselho === "outros" ? "Outros (especifique)" : conselho}
                </option>
              ))}
            </select>
            {errors.conselho && <span className="form-error">{errors.conselho.message}</span>}
          </div>

          {conselhoSelecionado === "outros" && (
            <div className="form-field">
              <label htmlFor="conselho_outro">Especifique o conselho</label>
              <input id="conselho_outro" {...register("conselho_outro")} />
              {errors.conselho_outro && (
                <span className="form-error">{errors.conselho_outro.message}</span>
              )}
            </div>
          )}

          <div className="form-field">
            <label htmlFor="numero_conselho">Número do conselho</label>
            <input id="numero_conselho" {...register("numero_conselho")} />
            {errors.numero_conselho && (
              <span className="form-error">{errors.numero_conselho.message}</span>
            )}
          </div>

          <div className="form-field">
            <label htmlFor="uf_conselho">UF do conselho</label>
            <select id="uf_conselho" defaultValue="" {...register("uf_conselho")}>
              <option value="" disabled>
                Selecione
              </option>
              {UFS.map((uf) => (
                <option key={uf} value={uf}>
                  {uf}
                </option>
              ))}
            </select>
            {errors.uf_conselho && <span className="form-error">{errors.uf_conselho.message}</span>}
          </div>
        </div>

        <div className="form-field">
          <label htmlFor="especialidade">Especialidade</label>
          <input id="especialidade" {...register("especialidade")} />
          {errors.especialidade && <span className="form-error">{errors.especialidade.message}</span>}
        </div>

        <div className="form-row">
          <div className="form-field">
            <label htmlFor="email">E-mail</label>
            <input id="email" type="email" {...register("email")} />
            {errors.email && <span className="form-error">{errors.email.message}</span>}
          </div>

          <div className="form-field">
            <label htmlFor="telefone">Telefone / WhatsApp</label>
            <input id="telefone" {...register("telefone")} />
            {errors.telefone && <span className="form-error">{errors.telefone.message}</span>}
          </div>
        </div>

        <div className="form-field">
          <label htmlFor="documento">Documento de identificação (PDF, JPG ou PNG)</label>
          <Controller
            control={control}
            name="documento"
            render={({ field: { onChange, name, ref } }) => (
              <input
                id="documento"
                name={name}
                ref={ref}
                type="file"
                accept=".pdf,.jpg,.jpeg,.png"
                onChange={(e) => onChange(e.target.files?.[0])}
              />
            )}
          />
          {errors.documento && <span className="form-error">{errors.documento.message}</span>}
        </div>

        <div className="form-field">
          <label htmlFor="foto_documento">Foto segurando o documento (JPG ou PNG)</label>
          <Controller
            control={control}
            name="foto_documento"
            render={({ field: { onChange, name, ref } }) => (
              <input
                id="foto_documento"
                name={name}
                ref={ref}
                type="file"
                accept=".jpg,.jpeg,.png"
                onChange={(e) => onChange(e.target.files?.[0])}
              />
            )}
          />
          {errors.foto_documento && (
            <span className="form-error">{errors.foto_documento.message}</span>
          )}
        </div>

        <div className="form-field form-checkbox">
          <label>
            <input type="checkbox" {...register("consentimento_lgpd")} />
            Declaro estar ciente e autorizo o tratamento dos dados pessoais e documentos enviados
            exclusivamente para finalidade de validação e liberação de acesso.
          </label>
          {errors.consentimento_lgpd && (
            <span className="form-error">{errors.consentimento_lgpd.message}</span>
          )}
        </div>

        {erroEnvio && <div className="form-error form-error-geral">{erroEnvio}</div>}

        <button type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Enviando..." : "Enviar solicitação"}
        </button>
      </form>
    </div>
  );
}
