// Build editable reference decks from the app's canonical template plans.
// ARTIFACT_TOOL_NODE_MODULES points to a supplied @oai/artifact-tool runtime.
import fs from 'node:fs/promises';
import path from 'node:path';
import { pathToFileURL, fileURLToPath } from 'node:url';

const moduleRoot = process.env.ARTIFACT_TOOL_NODE_MODULES;
if (!moduleRoot) throw new Error('Set ARTIFACT_TOOL_NODE_MODULES to the supplied Node.js packages.');
const { Presentation, PresentationFile } = await import(pathToFileURL(
  path.join(moduleRoot, '@oai/artifact-tool/dist/artifact_tool.mjs')).href);
const [plansPath, destination] = process.argv.slice(2);
if (!plansPath || !destination) throw new Error('Usage: build_template_decks.mjs plans.json staging-directory');
const plans = JSON.parse(await fs.readFile(plansPath, 'utf8'));
await fs.mkdir(destination, { recursive: true });
for (const [preset, pages] of Object.entries(plans)) {
  const presentation = Presentation.create({ slideSize: { width: 1280, height: 720 } });
  for (const page of pages) {
    const slide = presentation.slides.add();
    slide.background.fill = page.background;
    for (const [index, item] of page.elements.entries()) {
      const box = slide.shapes.add({ geometry: 'textbox', name: `${page.kind}-${index}`,
        position: { left: item.x, top: item.y, width: item.width, height: item.height },
        fill: 'none', line: { fill: 'none', width: 0 } });
      box.text = item.text;
      box.text.style = { typeface: page.font, fontSize: item.size, color: item.color,
        bold: item.bold, italic: item.italic, alignment: item.align, autoFit: 'none' };
    }
    if (page.image) {
      const imagePath = fileURLToPath(page.image);
      const image = await fs.readFile(imagePath);
      const region = page.image_box;
      slide.images.add({ blob: image, contentType: imagePath.endsWith('.svg') ? 'image/svg+xml' : 'image/png',
        alt: 'Hình minh họa mẫu BiliClass', fit: 'contain',
        position: { left: region.x, top: region.y, width: region.width, height: region.height } });
    }
    slide.speakerNotes.textFrame.setText(`Mẫu ${preset}: ${page.kind}. Ví dụ minh họa thiết kế từ app/assets/templates/demo_lessons.json. Khi tạo bài, thay bằng nội dung và hình của tài liệu giáo viên; không sao chép kiến thức của bài minh họa sang môn khác.`);
  }
  await (await PresentationFile.exportPptx(presentation)).save(path.join(destination, `${preset}-candidate.pptx`));
  console.log(`Created ${preset}: ${pages.length} editable slides`);
}
