import React from 'react';
import { Link } from 'react-router-dom';

const mainColor = '#007BFF';
const accentColor = '#FFC107';
const greenColor = '#43B66F';
const baseBg = '#F5F7FA';
const dark = '#222';
const maxWidth = 1000;

const sectionStyle = (bg: string = '#fff') => ({
  background: bg,
  padding: '80px 20px',
  display: 'flex',
  justifyContent: 'center',
});

const containerStyle = {
  maxWidth,
  width: '100%',
  margin: '0 auto',
};

const headingStyle = {
  fontFamily: "'Montserrat', 'Noto Sans JP', sans-serif",
  fontWeight: 700,
  fontSize: '2.2rem',
  textAlign: 'center' as const,
  marginBottom: '1.5rem',
  color: dark,
  letterSpacing: '0.01em',
};

const subHeadingStyle = {
  fontFamily: "'Montserrat', 'Noto Sans JP', sans-serif",
  fontWeight: 600,
  fontSize: '1.1rem',
  textAlign: 'center' as const,
  marginBottom: '2.5rem',
  color: '#555',
};

const cardGridStyle = {
  display: 'flex',
  gap: '2rem',
  flexWrap: 'wrap' as const,
  justifyContent: 'center',
};

const cardStyle = {
  background: '#fff',
  borderRadius: 16,
  boxShadow: '0 2px 12px rgba(0,0,0,0.06)',
  border: `1.5px solid #e5e7eb`,
  padding: '2rem 1.2rem',
  minWidth: 240,
  maxWidth: 320,
  flex: '1 1 260px',
  display: 'flex',
  flexDirection: 'column' as const,
  alignItems: 'center',
  transition: 'box-shadow 0.2s, border-color 0.2s, transform 0.2s',
};

const iconCircleStyle = (color: string) => ({
  width: 56,
  height: 56,
  borderRadius: '50%',
  background: color,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  marginBottom: 18,
  color: '#fff',
  fontSize: 28,
  boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
});

const ctaButtonStyle = {
  padding: '16px 40px',
  fontSize: '1.2rem',
  fontWeight: 700,
  background: '#fff',
  color: mainColor,
  border: `2px solid ${mainColor}`,
  borderRadius: 8,
  cursor: 'pointer',
  transition: 'all 0.2s',
  margin: '0 0.5rem',
};

const ctaButtonPrimaryStyle = {
  ...ctaButtonStyle,
  background: mainColor,
  color: '#fff',
  border: `2px solid ${mainColor}`,
};

const footerStyle = {
  background: dark,
  color: '#ccc',
  textAlign: 'center' as const,
  padding: '48px 20px 32px 20px',
  fontSize: '1rem',
  marginTop: 80,
};

export default function Home() {
  return (
    <div style={{ fontFamily: "'Noto Sans JP', 'Montserrat', sans-serif", background: baseBg }}>
      {/* ヒーロー */}
      <section
        style={{
          ...sectionStyle(`linear-gradient(120deg, ${mainColor} 0%, #0056b3 100%)`),
          minHeight: '70vh',
          alignItems: 'center',
          flexDirection: 'column',
          color: '#fff',
          position: 'relative',
        }}
      >
        <div style={{ ...containerStyle, textAlign: 'center', marginTop: 40 }}>
          <h1 style={{
            fontFamily: "'Montserrat', 'Noto Sans JP', sans-serif",
            fontWeight: 800,
            fontSize: '3.2rem',
            marginBottom: '1.2rem',
            letterSpacing: '0.01em',
            color: '#fff',
          }}>
            データ提供者に適切な報酬を
          </h1>
          <div style={{
            fontSize: '1.3rem',
            fontWeight: 500,
            marginBottom: '2.5rem',
            color: '#e3e9f3',
          }}>
            AIの時代だからこそ、正確なAIを
          </div>
          <div>
            <Link to="/signup" style={{ textDecoration: 'none' }}>
              <button style={ctaButtonPrimaryStyle}>無料で試す</button>
            </Link>
            <a href="#problems" style={{ textDecoration: 'none' }}>
              <button style={ctaButtonStyle}>詳しく見る</button>
            </a>
          </div>
        </div>
        {/* 下向き矢印 */}
        <div style={{
          position: 'absolute', left: '50%', bottom: 24, transform: 'translateX(-50%)',
          opacity: 0.5, fontSize: 36,
        }}>
          ▼
        </div>
      </section>

      {/* 課題提起 */}
      <section id="problems" style={sectionStyle(baseBg)}>
        <div style={containerStyle}>
          <h2 style={headingStyle}>AI時代の情報収集に潜む課題</h2>
          <div style={subHeadingStyle}>
            現在、多くのAIモデルはインターネットから情報を取得しています。しかし、その裏にはさまざまな問題が隠れています。
          </div>
          <div style={cardGridStyle}>
            <div style={cardStyle}>
              <div style={iconCircleStyle(mainColor)}>
                <span className="fa fa-user"></span>
              </div>
              <h3 style={{ fontWeight: 700, fontSize: '1.1rem', marginBottom: 8 }}>情報提供者への報酬がない</h3>
              <p style={{ color: '#444', fontWeight: 400, fontSize: '1rem', margin: 0 }}>
                多くのWebサイトやブログなどの情報提供者は、AIモデルにデータを利用されても報酬を得られていません。
              </p>
            </div>
            <div style={cardStyle}>
              <div style={iconCircleStyle(accentColor)}>
                <span className="fa fa-shield-alt"></span>
              </div>
              <h3 style={{ fontWeight: 700, fontSize: '1.1rem', marginBottom: 8 }}>情報の正確性と法的リスク</h3>
              <p style={{ color: '#444', fontWeight: 400, fontSize: '1rem', margin: 0 }}>
                フェイクニュースや古い情報が流通し、AIが誤情報を学習してしまうリスクが高まっています。
              </p>
            </div>
            <div style={cardStyle}>
              <div style={iconCircleStyle('#FF6B6B')}>
                <span className="fa fa-globe"></span>
              </div>
              <h3 style={{ fontWeight: 700, fontSize: '1.1rem', marginBottom: 8 }}>Webクローリングの制約</h3>
              <p style={{ color: '#444', fontWeight: 400, fontSize: '1rem', margin: 0 }}>
                GPTBot のブロックやサーバー負荷による DDoS リスクが存在し、充分なデータ取得が困難です。
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ソリューション：ジグザグレイアウト＋パララックス風アイコン */}
      <section className="solution-section" style={{ background: '#fff', padding: '80px 0' }}>
        <div className="section-header" style={{ ...containerStyle, marginBottom: 56 }}>
          <h2 style={{ ...headingStyle, color: dark }}>私たちのソリューション</h2>
          <p style={{ ...subHeadingStyle, color: '#555', marginBottom: 0 }}>
            Factify は、AI 開発の“データ提供・利用”双方を⾒える化し、安心・安全な環境を実現します。
          </p>
        </div>
        {/* 01. ライセンス保証 */}
        <div className="solution-item left" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', flexWrap: 'wrap', margin: '0 auto 56px', maxWidth: 900 }}>
          <div className="solution-text" style={{ flex: 1, minWidth: 280, padding: '0 2rem' }}>
            <h3 style={{ fontSize: '1.5rem', fontWeight: 700, color: mainColor, marginBottom: 12 }}>01. ライセンス保証</h3>
            <p style={{ fontSize: '1.05rem', color: '#333', lineHeight: 1.8 }}>
              著作権をクリアしたデータのみを厳選して収集。API レスポンスに「ライセンス情報」や「利用条件」が付与されるので、開発者は安心して AI モデルに学習データを読ませることができます。
            </p>
          </div>
          <div className="solution-graphic" style={{ flex: 1, minWidth: 220, display: 'flex', justifyContent: 'center', alignItems: 'center', padding: '1.5rem 0' }}>
            <div className="icon-wrapper rise-on-scroll" style={{ width: 120, height: 120, borderRadius: '50%', background: '#F5F7FA', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 4px 24px rgba(0,0,0,0.08)', transform: 'translateY(0)', transition: 'transform 0.6s cubic-bezier(.4,2,.6,1)' }}>
              <div style={{ width: 60, height: 60, borderRadius: '50%', background: mainColor, opacity: 0.2 }} />
            </div>
          </div>
        </div>
        {/* 02. 報酬還元 */}
        <div className="solution-item right" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', flexWrap: 'wrap-reverse', margin: '0 auto 56px', maxWidth: 900 }}>
          <div className="solution-graphic" style={{ flex: 1, minWidth: 220, display: 'flex', justifyContent: 'center', alignItems: 'center', padding: '1.5rem 0' }}>
            <div className="icon-wrapper rise-on-scroll" style={{ width: 120, height: 120, borderRadius: '50%', background: '#F5F7FA', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 4px 24px rgba(0,0,0,0.08)', transform: 'translateY(0)', transition: 'transform 0.6s cubic-bezier(.4,2,.6,1)' }}>
              <div style={{ width: 60, height: 60, borderRadius: '50%', background: accentColor, opacity: 0.2 }} />
            </div>
          </div>
          <div className="solution-text" style={{ flex: 1, minWidth: 280, padding: '0 2rem' }}>
            <h3 style={{ fontSize: '1.5rem', fontWeight: 700, color: accentColor, marginBottom: 12 }}>02. 確実な報酬還元</h3>
            <p style={{ fontSize: '1.05rem', color: '#333', lineHeight: 1.8 }}>
              データ提供者には「トークン」「ポイント」「キャッシュバック」などを柔軟に還元する仕組みを提供。<br />
              ブロガー・研究者・企業が安心してデータを提供できるよう、リアルタイムで還元状況をダッシュボードから確認できます。
            </p>
          </div>
        </div>
        {/* 03. ファクトチェック体制 */}
        <div className="solution-item left" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', flexWrap: 'wrap', margin: '0 auto 56px', maxWidth: 900 }}>
          <div className="solution-text" style={{ flex: 1, minWidth: 280, padding: '0 2rem' }}>
            <h3 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#FF6B6B', marginBottom: 12 }}>03. ファクトチェック体制</h3>
            <p style={{ fontSize: '1.05rem', color: '#333', lineHeight: 1.8 }}>
              AIの検知だけに頼らず、人間の視点での客観的な確認を加えることで、誤情報の混入を防ぎます。<br />
              確認後の「ファクトチェックタグ」は、APIレスポンスに付与され、<br />
              モデル学習時のフィルタリングにも活用可能です。
            </p>
          </div>
          <div className="solution-graphic" style={{ flex: 1, minWidth: 220, display: 'flex', justifyContent: 'center', alignItems: 'center', padding: '1.5rem 0' }}>
            <div className="icon-wrapper rise-on-scroll" style={{ width: 120, height: 120, borderRadius: '50%', background: '#F5F7FA', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 4px 24px rgba(0,0,0,0.08)', transform: 'translateY(0)', transition: 'transform 0.6s cubic-bezier(.4,2,.6,1)' }}>
              <div style={{ width: 60, height: 60, borderRadius: '50%', background: '#FF6B6B', opacity: 0.2 }} />
            </div>
          </div>
        </div>
        {/* 04. AI向け構造化 */}
        <div className="solution-item right" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', flexWrap: 'wrap-reverse', margin: '0 auto', maxWidth: 900 }}>
          <div className="solution-graphic" style={{ flex: 1, minWidth: 220, display: 'flex', justifyContent: 'center', alignItems: 'center', padding: '1.5rem 0' }}>
            <div className="icon-wrapper rise-on-scroll" style={{ width: 120, height: 120, borderRadius: '50%', background: '#F5F7FA', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 4px 24px rgba(0,0,0,0.08)', transform: 'translateY(0)', transition: 'transform 0.6s cubic-bezier(.4,2,.6,1)' }}>
              <div style={{ width: 60, height: 60, borderRadius: '50%', background: greenColor, opacity: 0.2 }} />
            </div>
          </div>
          <div className="solution-text" style={{ flex: 1, minWidth: 280, padding: '0 2rem' }}>
            <h3 style={{ fontSize: '1.5rem', fontWeight: 700, color: greenColor, marginBottom: 12 }}>04. AI向け構造化</h3>
            <p style={{ fontSize: '1.05rem', color: '#333', lineHeight: 1.8 }}>
              自然言語データをAIが読み込みやすい「JSON構造」や「メタデータ付きCSV」に自動変換。<br />
              さらに、医薬・ESG・行政文書など、専門領域ごとのタグ付けも行い、<br />
              モデル学習の精度と効率を飛躍的に高めます。
            </p>
          </div>
        </div>
      </section>

      {/* 選ばれる理由：番号付き3ポイント */}
      <section className="why-us-story" style={{ background: baseBg, padding: '80px 0' }}>
        <div className="section-header" style={{ ...containerStyle, marginBottom: 56 }}>
          <h2 style={{ ...headingStyle, color: dark }}>選ばれる理由</h2>
          <p style={{ ...subHeadingStyle, color: '#555', marginBottom: 0 }}>
            Factifyが選ばれる主な理由をご紹介します。
          </p>
        </div>
        <div className="why-story-container" style={{ maxWidth: 700, margin: '0 auto' }}>
          <div style={{ display: 'flex', alignItems: 'flex-start', marginBottom: 48 }}>
            <div style={{ flex: 0.2, textAlign: 'center', fontSize: 32, fontWeight: 700, color: accentColor, minWidth: 40 }}>1</div>
            <div style={{ flex: 0.8, textAlign: 'left', fontSize: '1.15rem', color: dark, fontWeight: 600, letterSpacing: '0.01em' }}>
              ファクトチェック済み・一次情報の提供で、誤学習リスクを大幅に軽減<br />
              <span style={{ fontWeight: 400, fontSize: '1.02rem', color: '#555', marginLeft: 8 }}>
                └ クローリングベースではない、高精度な学習用データを提供します。
              </span>
            </div>
          </div>
          <div style={{ display: 'flex', alignItems: 'flex-start', marginBottom: 48 }}>
            <div style={{ flex: 0.2, textAlign: 'center', fontSize: 32, fontWeight: 700, color: mainColor, minWidth: 40 }}>2</div>
            <div style={{ flex: 0.8, textAlign: 'left', fontSize: '1.15rem', color: dark, fontWeight: 600, letterSpacing: '0.01em' }}>
              明確なライセンス契約付きで、商用利用も安心<br />
              <span style={{ fontWeight: 400, fontSize: '1.02rem', color: '#555', marginLeft: 8 }}>
                └ 出典不明のデータによる法的リスクを回避できます。
              </span>
            </div>
          </div>
          <div style={{ display: 'flex', alignItems: 'flex-start', marginBottom: 0 }}>
            <div style={{ flex: 0.2, textAlign: 'center', fontSize: 32, fontWeight: 700, color: greenColor, minWidth: 40 }}>3</div>
            <div style={{ flex: 0.8, textAlign: 'left', fontSize: '1.15rem', color: dark, fontWeight: 600, letterSpacing: '0.01em' }}>
              情報提供者への収益還元スキームで、持続可能なデータ提供を実現<br />
              <span style={{ fontWeight: 400, fontSize: '1.02rem', color: '#555', marginLeft: 8 }}>
                └ キャッシュバックモデルにより、情報提供の質と量を継続的に確保できます。
              </span>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section style={{
        ...sectionStyle(mainColor),
        color: '#fff',
        textAlign: 'center',
        background: mainColor,
      }}>
        <div style={containerStyle}>
          <h2 style={{ ...headingStyle, color: '#fff', fontSize: '2.5rem' }}>今すぐ始めましょう</h2>
          <div style={{ fontSize: '1.25rem', marginBottom: '2rem', color: '#e3e9f3' }}>
            無料で試すか、お問い合わせページから詳細をお尋ねください。
          </div>
          <Link to="/signup" style={{ textDecoration: 'none' }}>
            <button style={ctaButtonPrimaryStyle}>無料で試してみる</button>
          </Link>
        </div>
      </section>

      {/* フッター */}
      <footer style={footerStyle}>
        <div style={{ maxWidth: 800, margin: '0 auto', fontSize: '0.95rem' }}>
          <div style={{ marginBottom: 16, fontWeight: 700, fontFamily: "'Montserrat', sans-serif" }}>
            Factify
          </div>
          <div style={{ marginBottom: 12 }}>
            <Link to="/about" style={{ color: '#ccc', margin: '0 0.5rem', textDecoration: 'none' }}>
              サービス概要
            </Link>
            |
            <Link to="/terms" style={{ color: '#ccc', margin: '0 0.5rem', textDecoration: 'none' }}>
              利用規約
            </Link>
            |
            <Link to="/privacy" style={{ color: '#ccc', margin: '0 0.5rem', textDecoration: 'none' }}>
              プライバシーポリシー
            </Link>
            |
            <Link to="/contact" style={{ color: '#ccc', margin: '0 0.5rem', textDecoration: 'none' }}>
              お問い合わせ
            </Link>
          </div>
          <div style={{ marginTop: 16 }}>
            <a href="https://twitter.com/yourprofile" style={{ color: '#ccc', margin: '0 0.5rem' }}>
              Twitter
            </a>
            <a href="https://facebook.com/yourprofile" style={{ color: '#ccc', margin: '0 0.5rem' }}>
              Facebook
            </a>
            <a href="https://linkedin.com/company/yourcompany" style={{ color: '#ccc', margin: '0 0.5rem' }}>
              LinkedIn
            </a>
          </div>
          <div style={{ marginTop: 24, fontSize: '0.85rem', color: '#888' }}>
            © 2025 Factify. All rights reserved.
          </div>
        </div>
      </footer>
    </div>
  );
}
