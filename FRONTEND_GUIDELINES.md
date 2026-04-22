# Frontend Development Guidelines

## Mobile-First Design Principle 📱

**重要**: フロントエンド修正・新規開発では、必ずモバイルファーストアプローチを採用する

### 実装フロー

1. **Base Styles (Mobile: 480px以下)**
   - モバイルデバイスを基準として、最小限のシンプルなスタイルから始める
   - 不要なアニメーション、複雑な配置は避ける
   - パディング・マージン・フォントサイズは小さめ

2. **Tablet Breakpoint (768px以上)**

   ```css
   @media (min-width: 768px) {
     /* タブレット用の調整 */
     /* グリッドを2列に、フォント・パディングを増加 */
   }
   ```

3. **Desktop Breakpoint (1024px以上)**
   ```css
   @media (min-width: 1024px) {
     /* デスクトップ用の最終形 */
     /* 3列グリッド、大きなフォント、max-width制限 */
   }
   ```

### CSS設計パターン

**✅ DO (モバイルファースト)**

```css
.component {
  /* Mobile base */
  padding: 1rem;
  font-size: 0.9rem;
  grid-template-columns: 1fr; /* 1列 */
}

@media (min-width: 768px) {
  .component {
    padding: 2rem;
    font-size: 1.1rem;
    grid-template-columns: repeat(2, 1fr); /* 2列 */
  }
}

@media (min-width: 1024px) {
  .component {
    grid-template-columns: repeat(3, 1fr); /* 3列 */
  }
}
```

**❌ DON'T (デスクトップファースト)**

```css
.component {
  /* Desktop base - then shrink for mobile */
  grid-template-columns: repeat(3, 1fr);
  padding: 4rem 2rem;
}

@media (max-width: 1024px) {
  .component {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .component {
    grid-template-columns: 1fr;
    padding: 1rem; /* ズレやすい */
  }
}
```

### チェックリスト

修正するたびに確認:

- [ ] モバイル基準で設計した？ (480px相当)
- [ ] 不要な!importantは削除した？
- [ ] グリッド・フレックスの方向はモバイルで1列から？
- [ ] パディング・フォントサイズはモバイルで小さめ？
- [ ] 768px/1024pxで段階的に大きくした？
- [ ] 実機テスト（480px, 768px, 1024px）した？

### 最近の成功例

**LandingPage.css (April 22, 2026)**

- Old: 1072行（デスクトップファースト、複雑）→ ズレが多発
- New: 400行（モバイルファースト） → クリーンで保守性向上

**CalendarPage.css**

- 480px完全対応: gap 0px, padding圧縮
- 768px+で段階的に拡大
- 横スクロールなし

### References

- MDN: https://developer.mozilla.org/en-US/docs/Mobile/Viewport_meta_tag
- CSS Cascade: https://web.dev/responsive-web-design-basics/

---

**作成日**: April 22, 2026  
**最終更新**: April 22, 2026
