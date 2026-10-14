from . import db


class RateioLancamento(db.Model):
    """Distribuição de uma despesa entre talhões, por percentual (RN005)."""
    __tablename__ = 'rateio_lancamento'

    id_rateio = db.Column(db.Integer, primary_key=True)

    id_lancamento = db.Column(
        db.String(36),
        db.ForeignKey('lancamento_financeiro.id_lancamento'),
        nullable=False
    )
    id_talhao = db.Column(
        db.Integer,
        db.ForeignKey('talhao.id_talhao'),
        nullable=False
    )
    percentual = db.Column(db.Numeric(5, 2), nullable=False)

    def __repr__(self):
        return f"<RateioLancamento talhao={self.id_talhao} {self.percentual}%>"
